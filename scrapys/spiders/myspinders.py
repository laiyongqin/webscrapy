# -*- coding: utf-8 -*-

import re
import scrapy
import json
import urllib2
import io
from scrapy import signals
from scrapys.items import TmallBrand
from scrapy.contrib.exporter import XmlItemExporter

class TmallBrandsSpider(scrapy.Spider):
    name = 'tmallbrands2'
    download_delay = 2
    start_urls = ['http://www.taobao.com']
    loginform = {
                 'callback': '1'
                 }
    f = io.open("myfile.tsv", "w+", encoding="utf8")
    needZiZhaoImg = False
    catIndustryIds = ["50025135:100","50025174:100","50025983:100","50023887:100","50025829:109","50026637:109","51052003:109","51042006:109","50072916:109","50108573:109","50108176:111","50026474:111","50026476:111","50026475:111","50026501:111","50026478:111","50026461:111","50023064:111","50026502:101","50026391:101","50026506:101","50026505:101","50026426:101","50026393:101","50020894:110","50020909:110","50043669:110","50022787:110","50024400:108","50024407:108","50024406:108","50043917:108","50099232:108","50024410:108","50094901:108","50024399:108","50024401:108","50047403:108","50047396:108","50900004:103","50892008:103","50902003:103","50886005:103","50894004:103","50067162:102","50067174:102","50051691:102","50097362:102","50030207:102","50030215:102","50030223:102","50069204:102","50067917:102","50030787:102","50030221:102","50030212:102","50030224:102","50030203:102","50024531:104","50072436:104","50036568:104","50036640:104","50072285:104","50067939:104","50043479:101","50074804:107","50074933:107","50100151:107","50100152:107","50100153:107","50100154:107","50099890:107","50099887:107","50100167:107","50100166:107","50099298:107","50072046:107","50072044:107","50074917:107","50025137:105","50023647:105","50029253:105","50036697:105","50024803:105","50033500:105","50106135:106","50029854:106","50029838:106","50029836:106","50029852:106","50070355:106","50076263:106","50029840:106","50044102:106"]
    brandIdMap = dict()
    exporter = XmlItemExporter(file)
    
    def __init__(self, category=None, *args, **kwargs):
        self.loginform['TPL_username'] = raw_input("username:")
        self.loginform['TPL_password'] = raw_input("password:")
        print self.loginform

    def start_requests(self):
        print "=="*10+" step 1 " + "="*10
        yield scrapy.FormRequest("https://login.taobao.com/member/login.jhtml",
                    formdata=self.loginform, callback=self.login_step2)
        
    # If need to input checkCode
    def login_step2(self, response):
        print "=="*10 +" step 2 " + "="*10
        text = response.body.decode("gbk", 'ignore')
        result = json.loads(text)
        print "=="*10 + "result: ", result
        if not result["state"]:
            print "failed to login in, error message: ",result["message"]
            data = result['data']
            print data["code"]
            print type(data["code"])
            print data["code"] == 3425
            if data["code"] == 3425 or data["code"] == 1000:
                checkCode = self.getCheckCode(data['ccurl'])    
                print "---"*10 + checkCode
                self.loginform['TPL_checkcode'] = checkCode
                self.loginform['need_check_code'] = 'true'
                formm = self.loginform
                print formm
                yield scrapy.FormRequest("https://login.taobao.com/member/login.jhtml",
                                         formdata=self.loginform, callback=self.login_step2)
        else:
            print "successfully login in!"
            yield scrapy.Request("https://passport.alipay.com/mini_apply_st.js?site=0&token=%s&callback=stCallback6"%result['data']['token'], callback=self.login_step3, encoding='gbk')
            
        
    def login_step3(self, response):
        print "=="*10+" step 3 " + "="*10
        st=re.search(r'"st":"(\S*)"( |})',response.body).group(1)
        print st
        yield scrapy.Request("http://login.taobao.com/member/vst.htm?st=%s"%st, callback=self.parse_start, encoding='gbk')

    def getCheckCode(self, url):
        print "+"*20+"getCheckCode"+"+"*20
        response = urllib2.urlopen(url)
        status = response.getcode()
        picData = response.read()
        
        path = "/home/owen/checkcode.jpg"
        if status == 200:
            localPic = open(path, "wb+")
            localPic.write(picData)
            localPic.close() 
            print "please go to %s, open file"%path  
            checkCode = raw_input("input code:")
            #print checkCode, type(checkCode)
            return checkCode
        else:
            print "failed to get Check Code, status:", response.status
    
    def parse_start(self, response):
        print "=="*10+" step 4 " + "="*10
        # be 5
        for i in range(1): #TODO
            yield scrapy.FormRequest("http://sell.tmall.com/auction/goods/goods_on_sale.htm", formdata={"page": str(i+1)}, callback=self.parse_brandsInfoStart)

    def parse_brandsStart(self, response):
        print "=="*10+" step 5.0 " + "="*10
        for catIndId in self.catIndustryIds:
            arr = catIndId.split(":")
            yield scrapy.Request("http://list.tmall.com/ajax/allBrandShowForGaiBan.htm?t=0&cat=%(catId)s&sort=s&style=g&search_condition=2&from=sn_1_brand-qp&active=1&industryCatId=%(industryCatId)s"%{"catId": arr[0], "industryCatId": arr[1]}, callback=self.parse_prodListPage)

    def parse_brandsInfoStart(self, response):
        f = open("brands.txt", "r")
        brandsText = f.read()
        brandIdList = brandsText.split(",")
        for brandId in brandIdList:
            yield scrapy.Request("http://brand.tmall.com/brandInfo.htm?brandId=%s&type=0"%brandId, callback=self.parse_brand)

    def parse_prodListPage(self, response):
        print "=="*10+" step 5.0 " + "="*10
        text = response.body.decode("gbk", 'ignore')
        result = json.loads(text)
        print len(result)
        for brandInfo in result:
            burl = brandInfo["href"]
            print burl
            brandId = re.search('brand=(\d+)', burl).group(1)
            self.brandIdMap[brandId] = brandId

    def closed(self, reson):
        print "closed spider"
        #f = open("brands.txt", "wb+")
        #print f.write(str(self.brandIdMap.keys()))

    def parse_brand(self, response):
        print "=="*10+" step 7 " + "="*10 + "start"
        brandName = response.xpath('//ul[@class="brandWiki-con"]/li[1]/em/text()').extract()[0]
        shopListLi = response.xpath('//ul[@class="brandShop-slide-list clearfix"]/li/div')
        for shopLi in shopListLi:
            tmallBrand = TmallBrand()
            shopName = shopLi.xpath('.//h3/text()').extract()[0]
            shopUrl = shopLi.xpath('./a/@href').extract()[0]
            shopType = ""
            if shopName.find("旗舰".decode("utf8")) > -1:
                shopType = "旗舰店"
            elif shopName.find("专卖".decode("utf8")) > -1:
                shopType = "专卖店"
            else:
                shopType = "其它"
            tmallBrand['brandName'] = brandName
            tmallBrand['shopType'] = shopType
            tmallBrand["shopUrl"] = shopUrl
            tmallBrand["shopName"] = shopName
            print "shopName: %s"%shopName + " shopUrl: %s"%shopUrl
            yield scrapy.Request(shopUrl, callback=self.parse_shop, meta=dict(tmallBrand=tmallBrand))
    
    def parse_shop(self, response):
        print "=="*10+" step 8 " + "="*10 + "start"
        tmallBrand = response.meta['tmallBrand']
        print response.encoding
        shopInfo = response.xpath('//div[@id="shop-info"]')
        shopTemp = shopInfo.xpath('.//div[contains(@class, "extend")]/ul')
        llen = len(shopTemp.xpath('./li').extract())
        shopRateUrl = response.xpath('//li[@class="shopkeeper"]//a/@href').extract()[0].strip()
        if llen == 5:
            tmallBrand['companyName'] = shopTemp.xpath('./li[3]/div/text()').extract()[0].strip()
        elif llen == 6:
            tmallBrand['companyName'] = shopTemp.xpath('./li[4]/div/text()').extract()[0].strip()

        shopLocation = shopTemp.xpath('./li[@class="locus"]/div/text()').extract()[0].strip()
        print "shopLocation:" + shopLocation
        if shopLocation.find(",") > 0:
            tmallBrand['shopProvince'] = shopLocation.split(",")[0]
            tmallBrand['shopCity'] = shopLocation.split(",")[1].strip()
        else:
            tmallBrand['shopProvince'] = shopLocation
            
        #tmallBrand['wangwangUrl'] = "http://amos.alicdn.com/getcid.aw?spm=a1z10.1-b.1997427721.6.TW1mHd&v=3&site=cntaobao&groupid=0&s=1&uid=%s"%shopName
        ziZhaoUrlNode = response.xpath('//a[@class="tm-gsLink"]/@href')
        ziZhaoUrl = ""
        if len(ziZhaoUrlNode) > 0:
            ziZhaoUrl = ziZhaoUrlNode.extract()[0].strip()
        tmallBrand['ziZhaoUrl'] = ziZhaoUrl

        print "shopRateUrl:" + shopRateUrl
        yield scrapy.Request(shopRateUrl, callback=self.fetch_rate, meta=dict(tmallBrand=tmallBrand))
        
        print "end write"

    def fetch_rate(self, response):
        print "=="*10+" step 9 " + "="*10 + "start"
        tmallBrand = response.meta['tmallBrand']
        category = response.xpath('//li[@class="company"]/../li[2]/a/text()').extract()[0].strip()
        tradeCount = response.xpath('//div[@class="total"]/span[last()]/text()').extract()[0]
        tmallBrand['category'] = category
        tmallBrand['tradeCount'] = tradeCount
        print tmallBrand
        yield tmallBrand





