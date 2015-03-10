# -*- coding: utf-8 -*-

import re
import scrapy
import json
import urllib2
import io
from scrapys.items import TmallBrand
from scrapy.contrib.exporter import XmlItemExporter

class TmallBrandsSpider(scrapy.Spider):
    name = 'tmallbrands'
    download_delay = 2
    start_urls = ['http://www.taobao.com']
    loginform = {
                 'callback': '1'
                 }
    f = io.open("myfile.tsv", "w+", encoding="utf8")
    needZiZhaoImg = False
    exporter = XmlItemExporter(file)
    
    def __init__(self, category=None, *args, **kwargs):
        self.loginform['TPL_username'] = '13817166196'
        self.loginform['TPL_password'] = 'Blissjiaf0104$%'
        print self.loginform

    def spider_opened(self, spider):
    	file = open('tmall_brands.csv', 'wb+')
    	
    	self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file.close()

    
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
            yield scrapy.FormRequest("http://sell.tmall.com/auction/goods/goods_on_sale.htm", formdata={"page": str(i+1)}, callback=self.parse_brandsIndex)
    
    def parse_brandsIndex(self, response):
        print "=="*10+" step 5 " + "="*10
        for i in range(65,90):
            yield scrapy.Request("http://brand.tmall.com/azIndexInside.htm?firstLetter=%s"%chr(i), callback=self.parse_page)
    
    def parse_page(self, response):
        print "=="*10+" step 6 " + "="*10 + "start"
        #print response.body
        #print "=="*10+" step 6 " + "="*10 + "end"
        brandLis = response.xpath('//ul[@id="J_SearchResult"]/li')
        print len(brandLis)
        for brandLi in brandLis:
            aNode = brandLi.xpath('./a')
            url = aNode.xpath('./@href').extract()[0]
            text = aNode.xpath('./text()').extract()[0]
            #print text
            yield scrapy.Request(url, callback=self.parse_brand)
    
    def parse_brand(self, response):
        print "=="*10+" step 7 " + "="*10 + "start"
        tmallBrand = TmallBrand()
        
        brandName = response.xpath('//ul[@class="brandWiki-con"]/li[1]/em/text()').extract()[0]
        tmallBrand['brandName'] = brandName
        shopListLi = response.xpath('//ul[@class="brandShop-slide-list clearfix"]/li')
        for shopLi in shopListLi:
            shopName = shopLi.xpath('.//h3/text()').extract()[0]
            print shopName
            shopUrl = shopLi.xpath('./div/a/@href').extract()[0]
            yield scrapy.Request(shopUrl, callback=self.parse_shop, meta=dict(tmallBrand=tmallBrand))
    
    def parse_shop(self, response):
        print "=="*10+" step 8 " + "="*10 + "start"
        tmallBrand = response.meta['tmallBrand']
        print response.encoding
        shopInfo = response.xpath('//div[@id="shop-info"]')
        shopName = response.xpath('//a[@class="slogo-shopname"]/strong/text()').extract()[0]
        tmallBrand['shopName'] = shopName
        shopTemp = shopInfo.xpath('.//div[contains(@class, "extend")]/ul')
        shopRateUrl = response.xpath('//li[@class="shopkeeper"]//a/@href').extract()[0].strip()
        tmallBrand['companyName'] = shopTemp.xpath('./li[3]/div/text()').extract()[0].strip()
        tmallBrand['shopLocation'] = shopTemp.xpath('./li[4]/div/text()').extract()[0].strip()
        tmallBrand['wangwangUrl'] = "http://amos.alicdn.com/getcid.aw?spm=a1z10.1-b.1997427721.6.TW1mHd&v=3&site=cntaobao&groupid=0&s=1&uid=%s"%shopName
        ziZhaoUrlNode = response.xpath('//a[@class="tm-gsLink"]/@href')
        ziZhaoUrl = ""
        if len(ziZhaoUrlNode) > 0:
            ziZhaoUrl = ziZhaoUrlNode.extract()[0].strip()
        tmallBrand['ziZhaoUrl'] = ziZhaoUrl
        
        shopType = ""
        if shopName.find("旗舰".decode("utf8")) > -1:
            shopType = "旗舰店"
        elif shopName.find("专卖".decode("utf8")) > -1:
            shopType = "专卖店"
        else:
            shopType = "其它"
        tmallBrand['shopType'] = shopType

        print "shopRateUrl:" + shopRateUrl
        yield scrapy.Request(shopRateUrl, callback=self.fetch_rate, meta=dict(tmallBrand=tmallBrand))
        
        if self.needZiZhaoImg == True and len(ziZhaoUrl) > 0:
            xid = re.search("xid=(.*)$", ziZhaoUrl).group(1)
            yield scrapy.Request(ziZhaoUrl, callback=self.fetch_ziZhaoImg, meta=dict(xid=xid, shopName=shopName))
        
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

    
    def fetch_ziZhaoImg(self, response):
        print "=="*10+" step 10 " + "="*10 + "start"
        shopName = response.meta['shopName']
        xid = response.meta['xid']
        tbtoken = response.xpath('//input[@name="_tb_token_"]/@value').extract()[0]
        checkCode = self.getCheckCode("http://pin.aliyun.com/get_img?sessionid=ALI4e00ec7fa164bfa16c5762b9d7330ddf&identity=zhaoshang_sellermanager")
        url = 'http://zhaoshang.mall.taobao.com/maintaininfo/liangzhao.htm?_tb_token_=%(tbtoken)s&checkCode=%(checkCode)s&xid=%(xid)s'%{'xid': xid, 'tbtoken': tbtoken, 'checkCode': checkCode}
        print url
        yield scrapy.Request(url, callback=self.save_ziZhaoImg, meta=dict(shopName=shopName))
    
    def save_ziZhaoImg(self, response):
        print "=="*10+" step 11 " + "="*10 + "start"
        shopName = response.meta['shopName']
        imgNode = response.xpath('//div[@class="box-item img-box"]//img/@src').extract()
        if len(imgNode) > 0:
            imgUrl = imgNode[0]
        else:
            print "===="*20
            print response.body
            print "===="*20
            print "failed to get Image"
            return
        print "imgUrl:%s"%imgUrl
        req = urllib2.Request(imgUrl)
        res = urllib2.urlopen(req)
        fileName = "/home/owen/Tmall/" + shopName + '.png'
        f = open(fileName, 'wb+')
        f.write(res.read())
        f.close()
        print "saved file:" + fileName
        
        