# vmx_vmware_lab


1. install ansible
2. install ovftools
3, install pyVmomi, pyVim
4. clone repository
5. download vMX from Juniper networks
6. update variables
7. update inventory
- identify dc, storage
- update vault
- encrypt the vault
user@server:~/vmx_vmware_lab⟫ ansible-vault encrypt group_vars/vmware/vault.yml
New Vault password:
Confirm New Vault password:
Encryption successful

8. execute playbook
ansible-playbook -i mylab vm_configure_pb.yml --ask-vault-pass
