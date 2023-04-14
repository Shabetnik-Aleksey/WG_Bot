from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
import re
import settings

from create_bot import telegram_bot_sendtext


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
        self.interface_peer = settings.INTERFACE_PEER

    def init_connect_mikro(self):
        """
        Метод для установления соединения с ротуером
        """

        try:
            self.ssh = ConnectHandler(**self.mikrotik_router_1)
        except NetmikoTimeoutException:
            telegram_bot_sendtext(f'Ошибка, неудалось подключится к ротеру, проверьте его доступность')
        except NetmikoAuthenticationException:
            telegram_bot_sendtext(f'Ошибка, авторизации на роутере, проверьте логин/пароль')

    def init_disconnect_mikro(self):
        """
        Метод для закрытия установленного соединения
        :return:
        """

        self.ssh.disconnect()

    def create_new_users(self, ip_a, key, name_user):
        """
        Метод для создания нового пира на роутере
        :param ip_a:
        :param key:
        :param name_user:
        :return:
        """
        answer = self.ssh.send_command(f'/interface/wireguard/peers/add allowed-address={ip_a}/32 '
                                       f'interface={self.interface_peer} public-key="{key}" comment={name_user}')

        if answer:
            telegram_bot_sendtext(f"PEER не был создан! - {answer}")
            raise MikrotikFailed(f"PEER не был создан! - {answer}")

    def create_queue_users(self, name_user, tariff_speed=100, type_set='add', ip_a=0):
        """
        Метод для создания и установки queue на роутере
        :param name_user:
        :param tariff_speed:
        :param type_set:
        :param ip_a:
        :return:
        """

        if type_set == 'add':
            self.ssh.send_command(f'/queue simple/add name={name_user} queue=pcq-upload-default/pcq-download-default'
                                  f' max-limit={tariff_speed}/{tariff_speed} target={ip_a}/32 comment={name_user}')

        elif type_set == 'set':
            self.ssh.send_command(f'/queue simple/set "{name_user}" max-limit={tariff_speed}/{tariff_speed}')

    def get_free_ip(self):
        """
        Метод который определяет следующий свободный ip-address для создания нового пира
        :return:
        """

        dd = self.ssh.send_command(f'interface/wireguard/peers/print proplist=allowed-address brief')
        ip_a = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', dd)
        for i in range(1, 256):
            if f'{".".join(ip_a[0].split(".")[:3])}.{i}' not in ip_a:
                return f'{".".join(ip_a[0].split(".")[:3])}.{i}'

        telegram_bot_sendtext(f"Свободный IP-Address для создания PEER не найден!")
        raise MikrotikFailed(f"Свободный IP-Address для создания PEER не найден!")

    def get_id_peers(self, user_name):
        """
        Метод для определения id peer
        :param user_name:
        :return:
        """

        id_peer = None
        dd = self.ssh.send_command(f'/interface/wireguard/peers/ print brief proplist=comment')
        id_peers = re.search(fr'{user_name}\n[\s]?(\d+)', dd)
        try:
            id_peer = id_peers.group(1)
        except AttributeError as err:
            telegram_bot_sendtext(f'Ошибка в поиске PEER ID не найден по имени {err}')
        return id_peer

    def change_state_peers(self, id_peer, state_peer='disable_peer', user_name=None):
        """
        Метод для изменения состояния peer, отключает, включает, удаляет
        :param id_peer:
        :param state_peer:
        :param user_name:
        :return:
        """

        if state_peer == 'disable_peer':
            self.ssh.send_command(f'/interface/wireguard/peers/disable numbers={id_peer}')
            if user_name:
                self.ssh.send_command(f'/queue/simple/disable "{user_name}"')

        elif state_peer == 'enable_manage_user':
            self.ssh.send_command(f'/interface/wireguard/peers/enable numbers={id_peer}')
            if user_name:
                self.ssh.send_command(f'/queue/simple/enable "{user_name}"')

        elif state_peer == 'delete_peer':
            self.ssh.send_command(f'/interface/wireguard/peers/remove numbers={id_peer}')
            if user_name:
                self.ssh.send_command(f'/queue/simple/remove "{user_name}"')

    def get_peers_all(self):
        """
        Метод который возвращает список всех пиров с детеилс, делает запись в файл, который отправляется в тг
        :return:
        """

        peers_all = self.ssh.send_command('/interface/wireguard/peers/ print detail')
        with open('all_users.txt', 'w') as f:
            f.write(peers_all)

    def get_system_resource(self):
        """
        Метод,который возвращает системные ресурсы роутера
        :return:
        """

        system_resource = self.ssh.send_command(f'/system/resource print').replace(' ', '')
        return system_resource

    def get_server_pub_key(self):
        """
        Метод,который возвращает системные ресурсы роутера
        :return:
        """

        system_resource = self.ssh.send_command(f'/interface/wireguard/print proplist=public-key val'
                                                f'ue-list').replace('public-key: ', '')
        return system_resource


class MikrotikFailed(Exception):
    """
    Это Хендлер для ошибок микротик
    """
    pass
