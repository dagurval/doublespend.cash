# Update vote information

- Requires a Bitcoin XT node running with this patch https://github.com/dgenr8/bitcoinxt/commit/62ec4ca3bba718668f0aab1dc5ff570f9441092f
- Node must be configured with txindex=1
- RPC username and password are assumed to be located at ../.bitcoin/bitcoin.conf

Depends on pygtail, jinja2 and simplejson python libraries.

On ubuntu:
sudo apt-get install python3-pygtail, python3-jinja2, python3-simplejson

Run doublespend.py to generate double spend data and update the static website.

# The website
The website itself consists of only static files. Point the webserver to serve files in folder site/

