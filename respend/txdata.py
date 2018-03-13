import simplejson as json
import hashlib
import glob
import os

TXDATA = "txdata"

def has_winner(respend):
    return respend['winner'] != None

def list_respends():
    return glob.glob(TXDATA + "/*.json")

def load_respend(path):
    with open(path) as fh:
        return json.load(fh)

def respend_id(txid_first, txid_second):
    h = hashlib.new('ripemd160')
    h.update(txid_first.encode() + txid_second.encode())
    return h.hexdigest()

def store_respend(respend):
    rid = respend_id(respend['first']['txid'], respend['second']['txid'])
    path = os.path.join(TXDATA, rid + ".json")
    with open(path, "w") as fh:
        json.dump(respend, fh, sort_keys = True, indent = 2 * ' ')
    return path
