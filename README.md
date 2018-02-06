# vmx_vmware_lab

#### Create VM templates

1. Install ansible
2. Install ovftools
3. Install pyVmomi, pyVim
4. Clone repository
5. Download vMX from Juniper networks
6. Update inventory
    - vi mylab/hosts
    - vi mylab/host_vars/vMX-01.yml
7. Update variables with valid storage, cluster, vCenter and datacenter
    - vi group_vars/all/vars.yml
    - vi group_vars/vmware/vars.yml
8. Update vault
    - vi group_vars/all/vault.yml
9. Encrypt the vault
    - ansible-vault encrypt group_vars/all/vault.yml
10. Execute playbook
    - ansible-playbook -i mylab vm_template_pb.yml --ask-vault-pass


#### Deploy vMX Virtual Machines

1. Update the variables with a valid cluster name and esx host ip where the VMs will be deployed.
    - vi group_vars/vmxlab/vars.yml
    
2. Run the playbook
ansible-playbook -i mylab vm_deployment_pb.yml --ask-vault-pass


#### Delete vMX Virtual Machines

1. Run the playbook
ansible-playbook -i mylab vm_delete_pb.yml --ask-vault-pass
