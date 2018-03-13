from respend.rpcutil import connection, JSONRPCException
from respend.txdata import list_respends, load_respend, store_respend, has_winner

def update_winners():
    changes = False
    print("Updating winners")

    for respend in list_respends():
        r = load_respend(respend)

        if has_winner(r):
            continue

        winner = check_winner(r)
        if winner:
            r['winner'] = winner
            store_respend(r)
            changes = True

    return changes

def check_winner(respend):
    try:
        rawtx = connection().getrawtransaction(respend['first']['txid'], 1)
        if "confirmations" in rawtx and rawtx['confirmations']:
            return "first"
    except JSONRPCException as e:
        pass

    try:
        rawtx = connection().getrawtransaction(respend['second']['txid'], 1)
        if "confirmations" in rawtx and rawtx['confirmations']:
            return "second"
    except JSONRPCException as e:
        pass
