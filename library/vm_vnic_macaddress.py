#!/usr/bin/env python

from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect
import atexit
import ssl
from ansible.module_utils.basic import *

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
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


def update_virtual_nic_state(si, vm_obj, nic_number, mac_addr):
    """
    :param si: Service Instance
    :param vm_obj: Virtual Machine Object
    :param nic_number: Network Interface Controller Number
    :param mac_addr: MAC address
    :return: True if success
    """
    nic_prefix_label = 'Network adapter '
    nic_label = nic_prefix_label + str(nic_number)
    virtual_nic_device = None
    for dev in vm_obj.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualEthernetCard) \
                and dev.deviceInfo.label == nic_label:
            virtual_nic_device = dev
    if not virtual_nic_device:
        raise RuntimeError('Virtual {} could not be found.'.format(nic_label))

    dev_changes = []
    virtual_nic_spec = vim.vm.device.VirtualDeviceSpec()
    virtual_nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    virtual_nic_spec.device = virtual_nic_device
    virtual_nic_spec.device.key = virtual_nic_device.key
    virtual_nic_spec.device.macAddress = virtual_nic_device.macAddress
    virtual_nic_spec.device.backing = virtual_nic_device.backing

    virtual_nic_spec.device.addressType = 'assigned'
    virtual_nic_spec.device.macAddress = mac_addr

    dev_changes.append(virtual_nic_spec)
    spec = vim.vm.ConfigSpec()
    spec.deviceChange = dev_changes
    task = vm_obj.ReconfigVM_Task(spec=spec)
    wait_for_tasks(si, [task])
    return True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vcenter_ip=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_password=dict(required=True, type='str', no_log=True),
            vport=dict(required=False, type='str', default='443'),
            vm_name=dict(required=True, type='str'),
            vnic=dict(required=True, type='str'),
            mac=dict(required=True, type='str')
        ),
        supports_check_mode=True,
    )

    # connect vSphere
    serviceInstance = SmartConnect(host=module.params['vcenter_ip'], user=module.params['vcenter_user'],
                                   pwd=module.params['vcenter_password'], port=module.params['vport'], sslContext=context)
    # disconnect vSphere
    atexit.register(Disconnect, serviceInstance)

    content = serviceInstance.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], module.params['vm_name'])

    if vm:
        update_virtual_nic_state(serviceInstance, vm, module.params['vnic'], module.params['mac'])
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="VM not found")


if __name__ == "__main__":
    main()
