
import collections
import time
import random

BootstrapEntry = collections.namedtuple('BootstrapEntry',
                                         ['transportId',
                                          'addr', # IP (or similar) address. None for automatic detection
                                          'port' # Extended information like port
                                         ])

_bootstrap_types = {}
def _registerBootstrap(bootstrapClass):
    _bootstrap_types[bootstrapClass.bootstrap_type] = bootstrapClass
    return bootstrapClass

def create(data):
    return _bootstrap_types[data['bsType']]()

@_registerBootstrap
class ManualBootstrap(object):
    bootstrap_type = 'manual'
    ui_bootstrap_name = 'Manual bootstrap'

    def start(self, assignedId, io_loop, getAdvertised, onFind):
        """ Start running on the specified io_loop """
        self.assignedId = assignedId
        self._onFind = onFind
        self._entries = []

    def renotify(self):
        """ Call onFind for all entries this bootstrap has found """
        for e in self._entries:
            self._onFind(e)

    @property
    def ui_entries(self):
        return self._entries

    def ui_addEntry(self, bse):
        assert isinstance(bse, BootstrapEntry)
        assert bse.addr
        self._entries.append(bse)
        self._onFind(bse)


# this destinations should be always reachable:
bs_servers = set([BootstrapEntry('anon-i2p',  '3WatglAk~f56TlMMIwVufUPKeByjaJVUSdAEaxlEU1vCmZAD4XSaGogU8Wl50olVxEZ5ipeps6iWUyWs8B49T1elbjcr0CaYnGSs~qq9kaRAcGbxXWA61bsTOdjviS3yTYTbdXkWeqFGdFZfSSMxBHmMlo~EZ46JPQBXkNB519MTF7oHuY0hUGVlfFHSoKdXCV7iM~mZSh1hupCM7NfnY3TvKK0EOv2TGiadznvuLkmvR3f5-1XaMYg-EU6tk2MrJhPGR5r9v~bK86rcnf0Z5TLJ66UqSw3-aINUu5jsmXnsYIBTl~8-FOWjbcQSP6kHUKGy2LCMJXUTfMxRE-3xr2d1ByCsYOmrJuSsyVlPVPCZpukcXTwqh3XUytulUGfQXkRphaRc7RTqCigIlcwCbZig2j9gWcYxjCOiuXogW1bPcabhC9CeWlOyvRa8ypMucU8nZKycIJWlNE-JFmJgzoIL1rWXtWAXeygH-eqi7tTK0Jp3RsW1Q2OqNdkk08ZpAAAA', ''), BootstrapEntry('anon-tor', 'd2paz3eimmfpek6t.onion:1337', '')])

@_registerBootstrap
class BootstrapWithServer(object):
    bootstrap_type = 'server'
    ui_bootstrap_name = 'Server bootstrap'

    def __init__(self, transport_id):
        self._transport_id = transport_id
        self._entries = []
        self._servers = []
        for serv in bs_servers:
            if serv.transportId == self._transport_id:
                self._servers.append(serv)
        self._updateTimeout = 30

    def start(self, assignedId, io_loop, getAdvertised, onFind):
        """ Start running on the specified io_loop """
        self.assignedId = assignedId
        self._io_loop = io_loop
        self._onFind = onFind
        self._periodicServerConnect()

    def renotify(self):
        """ Call onFind for all entries this bootstrap has found """
        for e in self._entries:
            self._onFind(e)

    @property
    def ui_entries(self):
        return self._entries

    def addEntry(self, bse):
        assert isinstance(bse, BootstrapEntry)
        assert bse.addr
        if self._entryAlreadyKnown(bse) == False:
            self._entries.append(bse)
            self._onFind(bse)

    def _entryAlreadyKnown(self, bse):
        for bs in self._entries:
            if bs.transportId == bse.transportId and bs.addr == bse.addr and bs.port == bse.port:
                return True
        return False

    def _periodicServerConnect(self):
        self._onFind(random.choice(self._servers))
        self._io_loop.add_timeout(time.time()+self._updateTimeout, self._periodicServerConnect)

    ui_addEntry = addEntry

