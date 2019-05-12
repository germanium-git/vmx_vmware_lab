#!/usr/bin/env python

from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
import atexit
import ssl
from ansible.module_utils.basic import *

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def wait_for_tasks(service_instance, tasks):
    property_collector = service_instance.content.propertyCollector
    task_list = [str(task) for task in tasks]
    # Create filter
    obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                 for task in tasks]
    property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                               pathSet=[],
                                                               all=True)
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_specs
    filter_spec.propSet = [property_spec]
    pcfilter = property_collector.CreateFilter(filter_spec, True)
    try:
        version, state = None, None
        # Loop looking for updates till the state moves to a completed state.
        while len(task_list):
            update = property_collector.WaitForUpdates(version)
            for filter_set in update.filterSet:
                for obj_set in filter_set.objectSet:
                    task = obj_set.obj
                    for change in obj_set.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if not str(task) in task_list:
                            continue

                        if state == vim.TaskInfo.State.success:
                            # Remove task from taskList
                            task_list.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            raise task.info.error
            # Move to next version
            version = update.version
    finally:
        if pcfilter:
            pcfilter.Destroy()


def add_nic(si, vm, network):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param network: Virtual Network

    It adds vnic of VXNET3 type, nic_spec.device = vim.vm.device.VirtualE1000() ic commented
    """
    spec = vim.vm.ConfigSpec()
    nic_changes = []

    nic_spec = vim.vm.device.VirtualDeviceSpec()
    nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

    nic_spec.device = vim.vm.device.VirtualVmxnet3()
    # nic_spec.device = vim.vm.device.VirtualE1000()

    nic_spec.device.deviceInfo = vim.Description()
    nic_spec.device.deviceInfo.summary = 'vCenter API test'

    nic_spec.device.backing = \
        vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    nic_spec.device.backing.useAutoDetect = False
    content = si.RetrieveContent()
    nic_spec.device.backing.network = get_obj(content, [vim.Network], network)
    nic_spec.device.backing.deviceName = network

    nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.connectable.allowGuestControl = True
    nic_spec.device.connectable.connected = False
    nic_spec.device.connectable.status = 'untried'
    nic_spec.device.wakeOnLanEnabled = True
    nic_spec.device.addressType = 'assigned'

    nic_changes.append(nic_spec)
    spec.deviceChange = nic_changes
    task = vm.ReconfigVM_Task(spec=spec)
    wait_for_tasks(si, [task])
    print "NIC CARD ADDED"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vcenter_ip=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_password=dict(required=True, type='str', no_log=True),
            vport=dict(required=False, type='str', default='443'),
            vm_name=dict(required=True, type='str'),
            vmnics=dict(required=True, type='dict'),
        ),
        supports_check_mode=True,
    )

    # connect vSphere
    si = SmartConnect(host=module.params['vcenter_ip'],
                      user=module.params['vcenter_user'],
                      pwd=module.params['vcenter_password'],
                      port=module.params['vport'],
                      sslContext=context)
    # disconnect vSphere
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], module.params['vm_name'])

    if vm:
        for vmnic in module.params['vmnics']:
            add_nic(si, vm, module.params['vmnics'][vmnic])
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="VM not found")


if __name__ == "__main__":
    main()

