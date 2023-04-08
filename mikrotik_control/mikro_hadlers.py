from netmiko import ConnectHandler
import re
import settings


class ControlMikrotik:
    def __init__(self):

        self.mikrotik_router_1 = {
            'device_type': 'mikrotik_routeros',
            'host': settings.HOST_MIKROTIK,
            'port': settings.PORT_MIKROTIK,
            'username': settings.LOGIN_MIKROTIK,
            'password': settings.PASS_MIKROTIK
        }
        self.ssh = None
        self.init_connect_mikro()
        self.interface_peer = 'wireguard_test'

    def init_connect_mikro(self):
        self.ssh = ConnectHandler(**self.mikrotik_router_1)

    def init_disconnect_mikro(self):
        self.ssh.disconnect()

    def create_new_users(self, ip_a, key, name_user):
        answer = self.ssh.send_command(f'/interface/wireguard/peers/add allowed-address={ip_a}/32 '
                                       f'interface={self.interface_peer} public-key="{key}" comment={name_user}')

        if answer:
            raise MikrotikFailed(f"PEER не был создан! - {answer}")

    def create_queue_users(self, ip_a, name_user):
        self.ssh.send_command(f'/queue simple/add name={name_user} queue=pcq-upload-default/pcq-download-default target'
                              f'={ip_a}/32 comment={name_user}')

    def get_free_ip(self):
        dd = self.ssh.send_command(f'interface/wireguard/peers/print proplist=allowed-address brief')
        ip_a = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', dd)
        for i in range(1, 256):
            if f'{".".join(ip_a[0].split(".")[:3])}.{i}' not in ip_a:
                return f'{".".join(ip_a[0].split(".")[:3])}.{i}'

        raise MikrotikFailed(f"Свободный IP Address для создания PEER не найден!")


class MikrotikFailed(Exception):
    pass
