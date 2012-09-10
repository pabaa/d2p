from .dtn import DTNTransport
from .p2p import P2PTransport
from .anon import AnonTransport

from . import netcorebase

class NetworkCore(netcorebase.AbstractNetCore):
    """ Manages the transports and associated endpoints.
    All initialization happens on the io_loop
     """
    def __init__(self, io_loop, cfg, projectManager=None):
        super(NetworkCore, self).__init__(projectManager)
        self._transports = [
            DTNTransport(io_loop, self, cfg),
            P2PTransport(io_loop, self, cfg),
            #AnonTransport(io_loop, self, cfg, 'I2P'),
            AnonTransport(io_loop, self, cfg, 'TOR')
        ]

    @property
    def ui_transports(self):
        return self._transports

    @property
    def ui_dtnTransport(self):
        res = self._transports[0]
        assert 'dtn' in res.transport_id
        return res

    @property
    def ui_p2pTransport(self):
        res = self._transports[1]
        assert 'p2p' in res.transport_id
        return res

    @property
    def ui_i2pTransport(self):
        res = self._transports[2]
        assert 'anon' in res.transport_id
        assert 'i2p' in res.transport_id
        return res

    @property
    def ui_torTransport(self):
        res = self._transports[2]
        assert 'anon' in res.transport_id
        assert 'tor' in res.transport_id
        return res

    def project_onLoad(self, project):
        """ Notify the project of all connected endpoints """
        for t in self._transports:
            t.project_onLoad(project)

    def transport_onNewEndpoint(self, transport, ep):
        for project in self._projectManager.values():
            project.handleEndpoint(ep)

    def _all_endpoints(self):
        for t in self._transports:
            for e in t.endpoints:
                yield e
