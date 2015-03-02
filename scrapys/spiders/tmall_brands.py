# -*- coding: utf-8 -*-

import re
import scrapy
import json
import urllib2
import io

class TmallBrandsSpider(scrapy.Spider):
    name = 'tmallbrands'
    download_delay = 2
    start_urls = ['http://www.taobao.com']
    loginform = {
                 'callback': '1'
                 }
    f = io.open("myfile.tsv", "w+", encoding="utf8")
    
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
        
        path = "/Users/Owen/checkcode.jpg"
        if status == 200:
            localPic = open(path, "wb+")
            localPic.write(picData)
            localPic.close() 
            print "please go to %s, open file"%path  
            checkCode = raw_input("input code:")
            print checkCode, type(checkCode)
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
        shopListLi = response.xpath('//ul[@class="brandShop-slide-list clearfix"]/li')
        for shopLi in shopListLi:
            shopName = shopLi.xpath('.//h3/text()').extract()[0]
            print shopName
            shopUrl = shopLi.xpath('./div/a/@href').extract()[0]
            yield scrapy.Request(shopUrl, callback=self.parse_shop)
    
    def parse_shop(self, response):
        print "=="*10+" step 8 " + "="*10 + "start"
        print response.encoding
        shopInfo = response.xpath('//div[@id="shop-info"]')
        shopName = response.xpath('//a[@class="slogo-shopname"]/strong/text()').extract()[0]
        shopTemp = shopInfo.xpath('.//div[contains(@class, "extend")]/ul')
        shopCompany = shopTemp.xpath('./li[3]/div/text()').extract()[0].strip()
        shopLocation = shopTemp.xpath('./li[4]/div/text()').extract()[0].strip()
        wangwangUrl = "http://amos.alicdn.com/getcid.aw?spm=a1z10.1-b.1997427721.6.TW1mHd&v=3&site=cntaobao&groupid=0&s=1&uid=%s"%shopName
        ziZhaoUrlNode = shopTemp.xpath('./li[5]/div/a/@href')
        ziZhaoUrl = ""
        if len(ziZhaoUrlNode) > 0:
            ziZhaoUrl = ziZhaoUrlNode.extract()[0].strip()
        string = shopName + "\t" + shopCompany + "\t" + shopLocation + "\t" + ziZhaoUrl + "\t" + wangwangUrl + "\n"
        print string
        self.f.write(string)
        self.f.flush()
        print "end write"
        
        
        