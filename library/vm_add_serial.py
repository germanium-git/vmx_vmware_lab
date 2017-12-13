#!/usr/bin/env python

from pyVmomi import vim
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



def create_telnet_serial_port(value):
    serial_spec = vim.vm.device.VirtualDeviceSpec()
    serial_spec.operation = 'add'
    serial_port = vim.vm.device.VirtualSerialPort()
    serial_port.yieldOnPoll = True

    backing = serial_port.URIBackingInfo()
    backing.serviceURI = 'telnet://:' + value
    backing.direction = 'server'
    serial_port.backing = backing
    serial_spec.device = serial_port
    return serial_spec



def add_serial(si, vm, port):
    """
    :param si: Service Instance
    :param vm: Virtual Machine Object
    :param port: Telnet port
    """

    # configure new telnet serial port
    serial_spec = create_telnet_serial_port(port)

    # apply configuration changes
    dev_changes = []
    dev_changes.append(serial_spec)

    # load empty config template applicable to VMs
    spec = vim.vm.ConfigSpec()
    spec.deviceChange = dev_changes

    # Update the VM
    task = vm.ReconfigVM_Task(spec=spec)
    tasks.wait_for_tasks(si, [task])



def main():
    module = AnsibleModule(
        argument_spec=dict(
            vcenter_ip=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_password=dict(required=True, type='str', no_log=True),
            vport=dict(required=False, type='str', default='443'),
            vm_name=dict(required=True, type='str'),
            telnet_port=dict(required=True, type='str'),
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
        add_serial(serviceInstance, vm, module.params['telnet_port'])
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="VM not found")


if __name__ == "__main__":
    main()
