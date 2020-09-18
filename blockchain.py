import sys
from pathlib import Path

from django.conf import settings
from multichaincli import Multichain

ACTIVE = 'makemigrations' not in sys.argv

if ACTIVE:
    rpchost = '172.20.0.4'
    chainname = settings.BLOCKCHAIN_NAME

    multichain_kwargs = {}

    #Read arguments from multichain.conf file
    conf_path = Path(f'~/.multichain/{chainname}/multichain.conf').expanduser()
    with conf_path.open() as f:
        for l in f.readlines():
            key = l[:l.index('=')]
            value = l[l.index('=')+1:].strip()
            multichain_kwargs[key] = value

    #Read arguments from params.conf file
    params_path = Path(f'~/.multichain/{chainname}/params.dat').expanduser()
    with params_path.open() as f:
        for l in f.readlines():
            if 'default-rpc-port' in l:
                multichain_kwargs['rpcport'] = l[l.index('=')+1:l.index('#')].strip()

    Blockchain = Multichain(multichain_kwargs['rpcuser'], multichain_kwargs['rpcpassword'],
        rpchost, multichain_kwargs['rpcport'], chainname)

else:
    class DummyBlockchain():
        pass
    Blockchain = DummyBlockchain()

class BlockchainMixin():

    @property
    def blockchain(self):
        return Blockchain