# vmx_vmware_lab

#### Create VM templates

1. install ansible
2. install ovftools
3. install pyVmomi, pyVim
4. clone repository
5. download vMX from Juniper networks
6. update inventory
    - vi mylab/hosts
    - vi mylab/host_vars/vMX-01.yml
7. update variables with valid storage, cluster, vCenter and datacenter
    - vi group_vars/all/vars.yml
    - vi group_vars/vmware/vars.yml
8. update vault
    - vi group_vars/all/vault.yml
9. encrypt the vault
    - ansible-vault encrypt group_vars/all/vault.yml
10. execute playbook
    - ansible-playbook -i mylab vm_template_pb.yml --ask-vault-pass


#### Deploy vMX Virtual Machines
WIP
ansible-playbook -i mylab vm_deployment_pb.yml --ask-vault-pass
