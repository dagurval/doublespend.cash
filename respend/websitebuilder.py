from respend.txdata import list_respends, load_respend, respend_id
from respend.rpcutil import get_cached_tx
import math
import datetime

ENTRIES_PER_PAGE = 10
   
def get_vout_value(tx, n):
    for vout in tx["vout"]:
        if vout["n"] == n:
            return vout["value"]

def sum_in_value(tx):
    value = 0
    for in_ in tx["vin"]:
        tx = get_cached_tx(in_["txid"])
        value += get_vout_value(tx, in_["vout"])
    return float(value)

def sum_out_value(tx):
    value = 0
    for out in tx["vout"]:
        value += out["value"]
    return value

def calc_fee(tx):
    COIN = 100_000_000
    value_in = sum_in_value(tx)
    value_out = sum_out_value(tx)
    return (value_in * COIN - value_out * COIN) / tx["size"]

def get_inputs(tx):
    inputs = [ ]
    for in_ in tx['vin']:
        txid = in_['txid']
        value = get_vout_value(get_cached_tx(txid), in_['vout'])
        inputs.append({
            "txid" : txid,
            "value" : value 
        })
    return inputs

def get_outputs(tx):
    outputs = [ ]
    for out in tx['vout']:
        addresses = [ ]
        if "scriptPubKey" in out and "addresses" in out['scriptPubKey']:
            addresses = out['scriptPubKey']['addresses']
        outputs.append({
            "addresses" : addresses,
            "value" : out['value']
        })
    return outputs

def find_tags(fee_per_byte, outputs):
    tags = set()
    
    if fee_per_byte < 1.0:
        tags.add("lowfee")

    # Known gambling addresses
    gambling = [
            # Satoshidice addresses (14/03/18)
            "bitcoincash:qz9cq5ylczhld5rm7a4px04zl50v5ahr3scyqudsp9",
            "bitcoincash:qz9cq5ytxmejfqqr0l5clkmw0l52pj6n5yc76lup7a",
            "bitcoincash:qz9cq5yfkyjpgq6xatlr6veyhmcartkyrg7wev9jzc",
            "bitcoincash:qz9cq5rlkdrjy2zkfzqscq847q9n07mu5y7hj8fcge",
            "bitcoincash:qz9cq5r294syv3csh56e4jpyqrpt7gl9lcj7wveruw",
            "bitcoincash:qz9cq5pcexrfnz0a60qz7xtvv8wh5rqf8v6pxd3k74",
            "bitcoincash:qz9cq5pgwgx68wfevx0t78xalkh33xa0v5wlx6nppx",
            "bitcoincash:qz9cq5pryv9hnqwa8q8mccmynk9uf4vlu5nxerpzmc",
            "bitcoincash:qz9cq5qa2mfqcxlc4220yh8fatadu4z7pcewq0ns8y",
            "bitcoincash:qz9cq5qeguz30nuynwt2ulq6cxt6gfklfv2djqj9lf",
            "bitcoincash:qqpx0wk0hru27l0xk2ek9xulhh269awklyauyuraxk",
    ];
    for out in outputs:
        for a in out['addresses']:
            if a in gambling:
                tags.add("gambling")
    return list(tags)
    

def extract_tx_info(tx):
    fee_per_byte = calc_fee(tx)
    outputs = get_outputs(tx)
    inputs = get_inputs(tx)

    return {
        "txid" : tx["txid"],
        "first_seen" : tx["first_seen"],
        "fee" : fee_per_byte,
        "inputs" : inputs,
        "outputs" : outputs,
        "tags" : find_tags(fee_per_byte, outputs)
    }

def seconds_between(first, second):
    # Seconds between seen
    def parse(date):
        return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    return (parse(second) - parse(first)).total_seconds()


def generate_respend_data():
    ids = list_respends()
    respends_raw = [ load_respend(r) for r in ids ]
    respends_raw.sort(key = lambda r: r['first']['first_seen'], reverse = True)

    # Extract the information we want
    respends = [ ]
    for r in respends_raw:

        try:
            first = extract_tx_info(r["first"])
            second = extract_tx_info(r["second"])
        except Exception as e:
            print(str(e))
            print("skiping respend")
            continue

        respends.append({
            "first" : first,
            "second" : second,
            "winner" : r["winner"],
            "seconds_between" : seconds_between(first['first_seen'], second['first_seen']),
            "id" : respend_id(first['txid'], second['txid']),
            })
    return respends

# Generates a short, colorful hash
def shortenhash(txid):
    prefix = txid[0:2]
    suffix = txid[-2:]
    middle = txid[2:-2]

    html = prefix;
    while len(middle):
        c = middle[0:4]
        middle = middle[4:]
        html += '<span class="hash" style="background-color: #%s">%s</span>' % (c, c)
    html += suffix
    return html

# Remove bitcoincash prefix
def addr_filter(addr):
    no_prefix = addr[len("bitcoincash:"):]
    return '<a href="https://blockchair.com/bitcoin-cash/address/%s">%s</a>' % (no_prefix, no_prefix)

def txid_filter(txid):
    shorten = shortenhash(txid)
    return '<a href="https://blockchair.com/bitcoin-cash/transaction/%s">%s</a>' % (txid, shorten)

def amount_filter(amount):
    return '<span class="amount">%.8f&nbsp;BCH</span>' % amount

def gen_pagination(curr, total):

    def gen_url(page):
        return "/%s.html#respends" % page

    items = [ ]
    items.append({ "title" : "Previous", "url" : None if curr == 1 else gen_url(curr - 1) })

    i = curr - 3 
    while len(items) < 9:
        if i < 1:
            i += 1
            continue
        if i > total:
            break
        items.append({ "title" : str(i), "url" : gen_url(i), "page" : i })
        i += 1

    items.append({ "title" : "Next", "url" : None if curr == total else gen_url(curr + 1) })
    return items

    


def build_website():
    from jinja2 import Template, Environment, select_autoescape, FileSystemLoader
    import os
    env = Environment(loader = FileSystemLoader("tpl/"))
    env.filters['addr'] = addr_filter
    env.filters['txid'] = txid_filter
    env.filters['bch'] = amount_filter

    template = env.get_template("base.html")
    data = generate_respend_data()
    pages = math.ceil(len(data) / ENTRIES_PER_PAGE)

    for p in range(pages):
        html = template.render(
                page = p + 1,
                pagination = gen_pagination(p + 1, pages),
                respends = data[:ENTRIES_PER_PAGE],
                time_now = datetime.datetime.utcnow())

        data = data[ENTRIES_PER_PAGE:]
    
        with open(os.path.join("site", "%s.html" % str(p + 1)), "w") as fh:
            fh.write(html)
        
        if p == 0:
            # also render page 1 as index.html
            with open(os.path.join("site", "index.html"), "w") as fh:
                fh.write(html)

