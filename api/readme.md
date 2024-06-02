# vpn setup

create docker network

```
docker network create --driver bridge --subnet 10.0.0.0/16 nextlabs
```

https://github.com/kylemanna/docker-openvpn

trik pro odheslovani certifikatu, not recommended, uprime je mi to jedno

openssl rsa -in /root/vpn/pki/private/ca.key -out /root/vpn/pki/private/ca.key.nopass
mv /root/vpn/pki/private/ca.key.nopass /root/vpn/pki/private/ca.key

todo delete
import pexpect

child = pexpect.spawn('docker exec -it <container_name> /path/to/revocation_script')
child.expect("Type the word 'yes' to continue, or any other input to abort.")
child.sendline("yes")
child.expect(pexpect.EOF)
