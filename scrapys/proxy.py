import random
import time

class ProxyMiddleware(object):
    data= []
    def process_request(self, request, spider):
        print "==" * 20 + " use proxy" + "=" * 10
        length = len(self.data)
        if len(self.data) == 0:
            f = open('config/proxy_list.txt','r')
            self.data = f.readlines()
        #print "length:" + str(length)
        index  = random.randint(0, length -1)
        item   = self.data[index]
        arr    = item.split(':')
        proxyUrl = 'http://%s:%s' % (arr[0],arr[1])
        print proxyUrl
        request.meta['proxy'] = proxyUrl 
