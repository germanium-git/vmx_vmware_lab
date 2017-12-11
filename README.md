# vmx_vmware_lab

#### Create VM templates

1. install ansible
2. install ovftools
3. install pyVmomi, pyVim
4. clone repository
5. download vMX from Juniper networks
6. update variables
7. update inventory
    - identify dc, storage
    - update vault
    - encrypt the vault
    user@server:~/vmx_vmware_lab⟫ ansible-vault encrypt group_vars/vmware/vault.yml
8. execute playbook
    - ansible-playbook -i mylab vm_template_pb.yml --ask-vault-pass


#### Deploy vMX Virtual Machines
WIP
ansible-playbook -i mylab vm_deployment_pb.yml --ask-vault-pass
