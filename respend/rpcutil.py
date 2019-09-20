import sys
sys.path.append("./lib/bitcoinrpc")
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from functools import lru_cache

def read_cfg(param):
    cfglines = open("../.bitcoin/bitcoin.conf").readlines()
    for c in cfglines:
        if c.startswith(param):
            return c[len(param) + 1:-1]
    return None

rpcuser = read_cfg("rpcuser")
rpcpassword = read_cfg("rpcpassword")
port = 8332

url = "http://%s:%s@127.0.0.1:%s" % (rpcuser, rpcpassword, port)
conn = AuthServiceProxy(url)

def connection():
    global conn
    return conn

@lru_cache(maxsize = 128)
def get_cached_tx(txid):
    return connection().getrawtransaction(txid, 1)
