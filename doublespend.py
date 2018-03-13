import sys
import time
from respend.logparser import RespendChecker
from respend.txdecoder import decode_tx
from respend.blockchain import BlockchainChecker
from respend.winnerupdater import update_winners
from respend.txdata import store_respend
from respend.websitebuilder import build_website

TXDATA = "txdata"

def on_respend_detected(tx1, tx2):
    tx1_decoded = decode_tx(tx1.hex)
    tx1_decoded['first_seen'] = tx1.time
    tx2_decoded = decode_tx(tx2.hex)
    tx2_decoded['first_seen'] = tx2.time

    print("Wrote %s" % store_respend({
        'first' : tx1_decoded,
        'second' : tx2_decoded,
        'timestamp' : tx1.time,
        'winner' : None}))

respend = RespendChecker(
        logpath = "debug-sample.log",
        on_respend = on_respend_detected)

blockchain = BlockchainChecker(
        on_new_tip = lambda: update_winners())

while True:
    update_website = respend.check()
    update_website |= blockchain.check()
    if update_website:
        print("New changes. Updating website.")
        build_website()

    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(1)
