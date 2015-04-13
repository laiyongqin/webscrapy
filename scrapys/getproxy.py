# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

class TmallProxySpider(CrawlSpider):
    name = 'getproxy'
    download_delay = 2
    start_urls = ['http://www.kuaidaili.com/proxylist/']
    rules = (
        Rule(LinkExtractor(allow=('proxylist/*', ), deny=('subsection\.php', )), callback='parse_item'),
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        #Rule(LinkExtractor(allow=('proxylist/*', )), callback='parse_item')
    )
    f = open("config/proxy_list2.txt", "w")
    
    def parse_item(self, response):
        print "=="*10 + "step 1" + "="*10
        trNodes = response.xpath('//div[@id="list"]/table/tbody/tr')
        print len(trNodes)
        for trNode in trNodes:
            ip = trNode.xpath('./td[1]/text()').extract()[0]
            port = trNode.xpath('./td[2]/text()').extract()[0]
            p = ip + ":" + port + "\n"
            print p
            self.f.write(p)
    
    def close(self, reason):
        print "close spider"
        self.f.close()