

import Client

DEFAULT_ANON = 'TOR'


class AnonEndpoint(object):
    def __init__(self, client, channel, destination):
        self._client = client
        self._channel = channel
        self._destination = destination

    @property
    def ui_remoteAddrStr(self):
        return destination

    def _read(self):
        pass

    def send(self, message):
        assert isinstance(message, bytes)
        self._client.ANON_send(self._channel, message)



class AnonTransport(Client.Client):
    def __init__(self, io_loop, netCore, cfg, anonymizer=DEFAULT_ANON):
        self.transport_id = '-'.join(['anon' , anonymizer])
        self._io_loop = io_loop
        self._netCore = netCore
        self._endpoints = []
        Client.Client.__init__(self, io_loop, anonymizer)

    def ANON_handle_newconnection(self, channel, destination_string):
        def Client.Client.ANON_handle_newconnection(channel, destination_string)

    def ANON_handle_connect_done(self, channel, dest):
        Client.Client.ANON_handle_connect_done(self, channel, dest)

    def ANON_handle_newmessage_noJSON_RPC(self, channel, message)
        Client.Client.ANON_handle_newmessage_noJSON_RPC(channel, message)

    @property
    def endpoints(self):
        return self._endpoints

    @property
    def ui_bootstraps(self):
        return self._bootstraps
        
