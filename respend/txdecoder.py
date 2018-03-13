from respend.rpcutil import connection

def decode_tx(hexstr):
    return connection().decoderawtransaction(hexstr)
