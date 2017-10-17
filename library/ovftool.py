#!/usr/bin/python


from ansible.module_utils.basic import *

def main():
    module = AnsibleModule(
        argument_spec=dict(
            ovftool_path=dict(required=True, type='str'),
            vcenter=dict(required=True, type='str'),
            vcenter_user=dict(required=True, type='str'),
            vcenter_password=dict(required=True, type='str', no_log=True),
            datacenter=dict(required=True, type='str'),
            cluster=dict(required=True, type='str'),
            datastore=dict(required=True, type='str'),
            ovf_network_vnic0=dict(required=False, type='str'),
            portgroup_vnic0=dict(required=False, type='str'),
            ovf_network_vnic1=dict(required=False, type='str'),
            portgroup_vnic1=dict(required=False, type='str'),
            path_to_ova=dict(required=True, type='str'),
            ova_file=dict(required=True, type='str'),
            vm_name=dict(required=False, type='str'),
            ssl_verify=dict(required=False, type='bool', default=True),
        ),
        supports_check_mode=True,
    )


    ovftool_exec = '{}ovftool'.format(module.params['ovftool_path'])
    ova_file = '{}/{}'.format(module.params['path_to_ova'], module.params['ova_file'])
    vi_string = 'vi://{}:{}@{}'.format(module.params['vcenter_user'],
                                                   module.params['vcenter_password'],
                                                   module.params['vcenter'])


    if len(module.params['datacenter'].strip())>0:
        vi_string += '/{}/host/{}'.format(module.params['datacenter'], module.params['cluster'])
    command_tokens = [ovftool_exec]

    if not module.params['ssl_verify']:
        command_tokens.append('--noSSLVerify')
    command_tokens.extend([
                        '--acceptAllEulas',
                        '--datastore={}'.format(module.params['datastore']),
                        '--name={}'.format(module.params['vm_name']),])

    if 'ovf_network_vnic0' in module.params.keys() and module.params['ovf_network_vnic0'] is not None and len(module.params['ovf_network_vnic0']) > 0:
        command_tokens.append('--net:{}={}'.format(module.params['ovf_network_vnic0'], module.params['portgroup_vnic0']))
    if 'ovf_network_vnic1' in module.params.keys() and module.params['ovf_network_vnic1'] is not None and len(module.params['ovf_network_vnic1']) > 0:
        command_tokens.append('--net:{}={}'.format(module.params['ovf_network_vnic1'], module.params['portgroup_vnic1']))

    command_tokens.extend([ova_file, vi_string])

    ova_tool_result = module.run_command(command_tokens)

    if ova_tool_result[0] != 0:
        module.fail_json(msg='Failed to deploy OVA, error message from ovftool is: {}'.format(ova_tool_result[1]))

    module.exit_json(changed=True, ova_tool_result=ova_tool_result)



if __name__ == '__main__':
    main()

