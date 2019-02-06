#!/usr/bin/env python

from pyVmomi import vim
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


def main():
    module = AnsibleModule(
        argument_spec=dict(
            vcenter_ip=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_password=dict(required=True, type='str', no_log=True),
            vport=dict(required=False, type='str', default='443'),
            vm_name=dict(required=True, type='str'),
        ),
        supports_check_mode=True,
    )


    # connect vSphere
    si = SmartConnect(host=module.params['vcenter_ip'], user=module.params['vcenter_user'],
                      pwd=module.params['vcenter_password'], port=module.params['vport'], sslContext=context)

    # disconnect vSphere
    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    vm = get_obj(content, [vim.VirtualMachine], module.params['vm_name'])

    if vm:
        vm.MarkAsTemplate()
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="VM not found")


if __name__ == "__main__":
    main()
