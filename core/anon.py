import functools
import time

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
    def __init__(self, io_loop, netCore, cfg, anonymizer=DEFAULT_ANON, debug=False):
        self.transport_id = 'anon-' + anonymizer.lower()
        self.netCore = netCore
        self._io_loop = io_loop
        self._endpoints = []
        self._bootstraps = []
        self._bootstraps_nextId = 0
        Client.Client.__init__(self, io_loop, anonymizer, debug)   

        p2pCfg = cfg.get('anon', {})
        bootstrapCfg = cfg.get('bootstraps', [{
            'bsType': 'manual',
        }])
        for bcfg in bootstrapCfg:
            bs = bootstrap.create(bcfg)
            self._addBootstrap(bs)  
        auto_bs = bootstrap.BootstrapWithServer(self.transport_id)
        self._addBootstrap(auto_bs)  

    def ANON_handle_newmessage_noJSON_RPC(self, channel, message):
        Client.Client.ANON_handle_newmessage_noJSON_RPC(self, channel, message)
        callback = functools.partial(self._handleNewmessage, channel, message, 1)
        self._io_loop.add_callback(callback)

    def ANON_handle_newmessage_response(self, channel, result, error, msg_id, request):
        Application.Application.ANON_handle_newmessage_response(
            self, channel, result, error, msg_id, request)
        bs = self._getAutoBootstrap()
        if request["method"] == "getPeerList":
            if "PeerList" in result:
                self.ow.out("Bootstrapping information received:\n", result)
                for dest in result["PeerList"]:
                    bs.addEntry(bootstrap.BootstrapEntry(self.transport_id, dest, ''))

    def _getAutoBootstrap(self):
        for bs in self._bootstraps:
            if bs.bootstrap_type == 'server':
                return bs

    def _handleNewmessage(self, channel, message, to):
        if to < 5:
            ep = self._getEndPoint(channel)
            if ep != None:
                if isinstance(message, ''.__class__):
                    message = message.encode('utf-8')
                ep.read(message)
                return
            else:
                callback = functools.partial(self._handleNewmessage, channel, message, to+1)
                self._io_loop.add_timeout(time.time()+5, callback)
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

    def _addBootstrap(self, bootstrap):
        bootstrap.start(self._bootstraps_nextId, self._io_loop, [], self._onBootstrapFoundEntry)
        self._bootstraps_nextId += 1
        self._bootstraps.append(bootstrap)

    ui_addBootstrap = _addBootstrap

    def _onBootstrapFoundEntry(self, bse):    
        if bse.transportId != self.transport_id:
            return # We don't support that type of connections
        if self.destination == bse.addr:
            return # We don't connect to ourselves
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
        for ep in self._endpoints:
            if ep.channel == channel:
                if dest == None or ep.addr == dest:
                    return ep
        return None

    @property
    def ui_serverDestination(self):
        return self.destination

    def project_onLoad(self, project):
        for e in self.endpoints:
            project.handleEndpoint(e)

    def onEndpointError(self, ep):
        self._endpoints.remove(ep)
        # TODO notify netCore about endpoint error
        
