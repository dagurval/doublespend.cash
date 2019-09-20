from respend.rpcutil import connection

class BlockchainChecker:
    def __init__(self, on_new_tip):
        self.on_new_tip = on_new_tip
        self.tip = None

    def check(self):
        try:
            new_tip = connection().getbestblockhash()
        except Exception as e:
            print("tip check failed: " + str(e))
            return False
        if new_tip == self.tip:
            return False
        print("New blockchain tip: %s" % new_tip)
        self.tip = new_tip
        return self.on_new_tip()
