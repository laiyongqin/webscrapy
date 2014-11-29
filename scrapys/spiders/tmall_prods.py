# -*- coding: utf-8 -*-

import re
import scrapy
import json
import urllib2
import io
from scrapys.items import ProdItem

class TmallSpider(scrapy.Spider):
    name = 'tmallgoods'
    download_delay = 1
    start_urls = ['http://www.taobao.com']
    loginform = {
                 'callback': '1'
                 }
    
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
        #print st
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
            yield scrapy.FormRequest("http://sell.tmall.com/auction/goods/goods_on_sale.htm", formdata={"page": str(i+1)}, callback=self.parse_goods)
    
    def parse_goods(self, response):
        print "=="*10+" step 5 " + "="*10
        goodsIds = response.xpath('//tr[@class="goods-sid"]//input[@name="selectedIds"]/@value').extract()
        for goodsId in goodsIds:
            type(goodsId)
            yield scrapy.Request("http://upload.tmall.com/auction/publish/edit.htm?spm=0.0.0.0.xmUVad&item_num_id=%s&auto=false"%goodsId, callback=self.parse_item)
            break
            
    def parse_item(self, response):
        print "=="*10+" step 6 " + "="*10
        f1 = io.open("/Users/Owen/test.html", "w+", encoding='utf8')
        f1.write(response.body.decode('gbk', 'ignore'))
        print "=="*10+" step 6 " + "="*10
        item = ProdItem()
        category = response.xpath('//div[@id="product-info"]/div/ul/li[1]/text()').extract()[0]
        item['category'] = category
        
        attrs = dict()
        attrBoxs = response.xpath('//li[@name="spus"]')
        for spu in attrBoxs:
            attrName = spu.xpath("label/text()").extract()[0]
            attrValue = ""
            if len(spu.xpath('.//ul[contains(@class, "J_ul-single")]')) > 0:
                attrValue = spu.xpath(".//option[@selected]/text()").extract()
            else:
                values = spu.xpath('.//ul[contains(@class, "J_ul-multi")]//input[@selected]/../label/text()').extract()
                if len(values) > 0:
                    for value in values:
                        attrValue = attrValue + value
            attrs[attrName] = attrValue 
        item['attrs'] = attrs
        
        skuBoxs = response.xpath('//li[@id="J_SellProperties"]//div[contains(@class, "sku-group")]')
        skus = dict()
        if len(skuBoxs) > 0:
            for skuBox in skuBoxs:
                skuGroupName = skuBox.xpath("@data-caption").extract()[0]
                skuItems = dict()
                skuItemBoxs = skuBox.xpath('.//input[@checked]')
                if len(skuItemBoxs) > 0:
                    for skuItemBox in skuItemBoxs:
                        itemOldName = skuItemBox.xpath('../label[@class="labelname"]/text()').extract()[0]
                        _itemNewName = skuItemBox.xpath('../input[last()]/@value').extract()
                        print _itemNewName
                        if len(_itemNewName) > 0:
                            skuItems[itemOldName] = _itemNewName[0]
                skus[skuGroupName] = skuItems
            item['skus'] = skus
                        
        print "=="*10+" item " + "="*10
        print item
        print "=="*10+" item " + "="*10
        