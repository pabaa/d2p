

from anon import Client
from anon import Application

from . import bootstrap

DEFAULT_ANON = 'TOR'


class AnonEndpoint(object):
    def __init__(self, client, channel, destination):
        self.client = client
        self.channel = channel
        self.addr = destination

    @property
    def ui_remoteAddrStr(self):
        return self.addr

    def read(self, message):
        self.client.netCore.onRecv(self, message)

    def send(self, message):
        assert isinstance(message, bytes)
        self.client.ANON_send(self.channel, message)


class AnonTransport(Client.Client):
    def __init__(self, io_loop, netCore, cfg, anonymizer=DEFAULT_ANON):
        self.transport_id = 'anon-' + anonymizer.lower()
        self.netCore = netCore
        self._io_loop = io_loop
        self._endpoints = []
        self._bootstraps = []
        self._bootstraps_nextId = 0
        Client.Client.__init__(self, io_loop, anonymizer)      

        p2pCfg = cfg.get('anon', {})
        bootstrapCfg = cfg.get('bootstraps', [{
            'bsType': 'manual',
        }])
        for bcfg in bootstrapCfg:
            bs = bootstrap.create(bcfg)
            self._addBootstrap(bs)  

    def ANON_handle_newmessage_noJSON_RPC(self, channel, message):
        Client.Client.ANON_handle_newmessage_noJSON_RPC(self, channel, message)
        self._io_loop.add_callback(self._handleNewmessage, channel, message, 1)

    def _handleNewmessage(self, channel, message, to):
        if to < 5:
            ep = self._getEndPoint(channel)
            if ep != None:
                if isinstance(message, ''.__class__):
                    message = message.encode('utf-8')
                ep.read(message)
                return
            else:
                self._io_loop.add_timeout(1, self._handleNewmessage, channel, message, to+1)
        else:
            print('Something went terribly wrong: ' + message + 'Channel: ' + str(channel) + ' Endpoints: ' + str(self._endpoints))
            

    def ANON_handle_newconnection(self, channel, destination_string):
        Client.Client.ANON_handle_newconnection(self, channel, destination_string)
        ep = AnonEndpoint(self, channel, destination_string)
        self._endpoints.append(ep)
        self.netCore.transport_onNewEndpoint(self, ep)

    @property
    def endpoints(self):
        return self._endpoints

    @property
    def ui_bootstraps(self):
        return self._bootstraps

    # todo?
    def _addBootstrap(self, bootstrap):
        bootstrap.start(self._bootstraps_nextId, self._io_loop, self._getBootstrapEntries, self._onBootstrapFoundEntry)
        self._bootstraps_nextId += 1
        self._bootstraps.append(bootstrap)

    ui_addBootstrap = _addBootstrap

    def _onBootstrapFoundEntry(self, bse):        
        if bse.transportId != self.transport_id:
            return # We don't support that type of connections
        # We're just connecting to anything we can find
        self._connectTo(bse.addr)

    def _connectTo(self, addr):
        self.ANON_connect(addr)

    def ANON_handle_connect_done(self, chan, dest):
        Client.Client.ANON_handle_connect_done(self, chan, dest)
        ep = AnonEndpoint(self, chan, dest)
        self._endpoints.append(ep)
        self.netCore.transport_onNewEndpoint(self, ep)

    def ANON_handle_connect_failed(self, dest):
        Client.Client.ANON_handle_connect_failed(self, dest)

    def ANON_handle_disconnected(self, channel, dest):
        Client.Client.ANON_handle_disconnected(self, channel, dest)
        ep = self._getEndPoint(channel, dest)
        if ep != None:
            self.onEndpointError(ep)

    def _getEndPoint(self, channel, dest=None):
        if dest == None:
            for ep in self._endpoints:
                print(str(ep.channel) + ' <> ' + str(channel) + ' ---- ' + str(ep.channel.__class__) + ' <> ' + str(channel.__class__))
                if ep.channel == channel:
                    return ep
        else:
            for ep in self._endpoints:
                if ep.channel == channel and ep.addr == dest:
                    return ep
        return None

    # todo, was passiert hier??
    def _getBootstrapEntries(self):
        return [bootstrap.BootstrapEntry(self.transport_id, None, self._localPort)]

    @property
    def ui_serverDestination(self):
        return self.destination

    def project_onLoad(self, project):
        for e in self.endpoints:
            project.handleEndpoint(e)

    def onEndpointError(self, ep):
        pass
        