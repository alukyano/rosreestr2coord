from __future__ import division, print_function
import proxy_handling
import urllib2

# Try to send request through a TOR
# try:
#     import socks  # SocksiPy module
#     import socket
#     SOCKS_PORT = 9150 # 9050
#     def create_connection(address, timeout=None, source_address=None):
#         sock = socks.socksocket()
#         sock.connect(address)
#         return sock
#     socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT)
#     socket.socket = socks.socksocket
#     socket.create_connection = create_connection
#     print("WITH PROXY")
# except:
#     pass

import socket
# import urllib
import math
from logger import logger


def y2lat(y):
    return (2 * math.atan(math.exp(y / 6378137)) - math.pi / 2) / (math.pi / 180)


def x2lon(x):
    return x / (math.pi / 180.0) / 6378137.0


def xy2lonlat(x, y):
    return [x2lon(x), y2lat(y)]


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'


class TimeoutException(Exception):
    pass


def make_tile_request(url, tile_mode="direct", static_proxy="none"):
    if url:
        url = url.encode('utf-8')
        logger.debug(url)
        if tile_mode == 'private' and static_proxy != 'none':
            return make_request_with_static_proxy(url,static_proxy)
        if tile_mode == 'public':
            proxies = proxy_handling.load_proxies()
            if proxies and len(proxies) and proxies[0] != 'None':
                return make_request_with_proxy(url)
        try:
            f = urllib2.urlopen(url)
            read = f.read()
            return read
        except Exception as er:
            logger.warning(er)
            raise TimeoutException()
    return False

def make_request(url, with_proxy=False, static_proxy="none"):
    # original function
    if url:
        url = url.encode('utf-8')
        logger.debug(url)
        if static_proxy != 'none':
            return make_request_with_static_proxy(url,static_proxy)
        if with_proxy:
            proxies = proxy_handling.load_proxies()
            if proxies and len(proxies) and proxies[0] != 'None':
                return make_request_with_proxy(url)
        try:
            f = urllib2.urlopen(url)
            read = f.read()
            return read
        except Exception as er:
            logger.warning(er)
            raise TimeoutException()
    return False

def make_request_with_static_proxy(url,static_proxy):
    if static_proxy != "none":
        try:
            print ("Using proxy: ", static_proxy)
            logger.info("Using proxy: %s", static_proxy)
            auth = urllib2.HTTPBasicAuthHandler()
            proxy_handler = urllib2.ProxyHandler({'http': static_proxy, 'https': static_proxy})
            opener = urllib2.build_opener(proxy_handler, auth, urllib2.HTTPHandler)
            urllib2.install_opener(opener)
#            logger.info("URL using proxy: %s", url)
            conn = urllib2.urlopen(url)
            read = conn.read()
#            print(read)
            return read
        except Exception as er:
            logger.warning(er)



def make_request_with_proxy(url):
    proxies = proxy_handling.load_proxies_from_file()
    if not proxies:
        proxy_handling.update_proxies()
        proxies = proxy_handling.load_proxies_from_file()
    removed = False
    tries = 3  # number of tries for each proxy
    for proxy in proxies:
        for i in range(1, tries+1):  # how many tries for each proxy
            try:
                print('%i iteration of proxy %s' % (i, proxy), end="")
                proxy_handler = urllib2.ProxyHandler({'http': proxy, 'https': proxy})
                opener = urllib2.build_opener(proxy_handler)
                urllib2.install_opener(opener)
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
                    'referer': 'htpps://www.google.com/'}
                request = urllib2.Request(url, headers=headers)
                f = urllib2.urlopen(request)
                read = f.read()
                return read
            except Exception as er:
                logger.warning(er)
            if i == tries:
                proxies.remove(proxy)
                removed = True
    if removed:
        proxy_handling.dump_proxies_to_file(proxies)
