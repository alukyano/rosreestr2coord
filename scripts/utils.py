from __future__ import division, print_function
import proxy_handling
import urllib
import urllib2
import base64

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


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
REFERER = 'https://pkk.rosreestr.ru/'


class TimeoutException(Exception):
    pass


def make_tile_request(url, tile_mode="direct", static_proxy="none"):
    if url:
        url = url.encode('utf-8')
        logger.debug(url)
        logger.debug("make_tile_request")
        if tile_mode == 'private' and static_proxy != 'none':
            return make_request_with_static_proxy(url,static_proxy)
        if tile_mode == 'public':
            proxies = proxy_handling.load_proxies()
            if proxies and len(proxies) and proxies[0] != 'None':
                return make_request_with_proxy(url)
        try:
            headers = {
                'user-agent': USER_AGENT,
                'referer': REFERER}
            request = urllib2.Request(url, headers=headers)            
            f = urllib2.urlopen(request)
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
        logger.debug("make_request")
        if static_proxy != 'none':
            return make_request_with_static_proxy(url,static_proxy)
        if with_proxy:
            proxies = proxy_handling.load_proxies()
            if proxies and len(proxies) and proxies[0] != 'None':
                return make_request_with_proxy(url)
        try:
            headers = {
                'user-agent': USER_AGENT,
                'referer': REFERER}
            request = urllib2.Request(url, headers=headers)
            conn = urllib2.urlopen(request)              
            read = conn.read()
            return read
        except Exception as er:
            logger.warning(er)
            raise TimeoutException()
    return False

def make_request_with_static_proxy(url,static_proxy):
    if static_proxy != "none":
        try:
            print ("Using static proxy: [", static_proxy, "]")
            logger.info("Using static proxy: %s", static_proxy)
#            auth = urllib2.HTTPBasicAuthHandler()
            proxy =static_proxy.split("@")[1]
#            auth_proxy = urllib2.ProxyBasicAuthHandler()
            
            proxy_handler = urllib2.ProxyHandler({'http': proxy, 'https': proxy})
#            password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            
            user = static_proxy.split("@")[0]
            user = user.split("/")[2]
            user_enc = base64.b64encode(bytes(user))
#            user1,pass1 = user.split(":")
#            print ("user=",user1,pass1,proxy)
#            password_manager.add_password(None, url, user1, pass1)
#            auth_proxy.add_password(None, url, user1, pass1)
#            auth_manager = urllib2.HTTPBasicAuthHandler(password_manager)
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
#            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            urllib2.install_opener(opener)
            headers = {
                'user-agent': USER_AGENT,
                'referer': REFERER,
                'Proxy-Authorization': 'Basic ' + user_enc}

            request = urllib2.Request(url, headers=headers)

            conn = urllib2.urlopen(request,timeout=3)  
#            logger.info("URL using static proxy: %s", url)
            read = conn.read()            
            return read

        except (urllib2.HTTPError, urllib2.URLError) as ex:
                print ("URLERROR:", str(ex))
                return
        except Exception as er:
            logger.warning(er)
            print("Exception: ", er)



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
                print('%i iteration of public proxy %s' % (i, proxy), end="")
                proxy_handler = urllib2.ProxyHandler({'http': proxy, 'https': proxy})
                opener = urllib2.build_opener(proxy_handler)
                urllib2.install_opener(opener)
                headers = {
                    'user-agent': USER_AGENT,
                    'referer': REFERER}
                request = urllib2.Request(url, headers=headers)
                print("URL using public proxy: ", url)  
                f = urllib2.urlopen(request,timeout=5)
                read = f.read()
                return read
            except Exception as er:
                logger.warning(er)
            if i == tries:
                proxies.remove(proxy)
                removed = True
    if removed:
        proxy_handling.dump_proxies_to_file(proxies)
