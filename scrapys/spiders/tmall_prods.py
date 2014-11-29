# -*- coding: utf-8 -*-

import re
import scrapy
import json
import urllib2

class TmallSpider(scrapy.Spider):
    name = 'tmallgoods'
    download_delay = 0.2
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
                yield scrapy.FormRequest("https://login.taobao.com/member/login.jhtml",
                    formdata=self.loginform, callback=self.login_step2)
        else:
            print "successfully login in!"
            yield scrapy.Request("https://passport.alipay.com/mini_apply_st.js?site=0&token=%s&callback=stCallback6"%result['data']['token'], callback=self.login_step3, encoding='gbk')
        
    def login_step3(self, response):
        print "=="*10+" step 3 " + "="*10
        st=re.search(r'"st":"(\S*)"( |})',response.body).group(1)
        #print st
        yield scrapy.Request("http://login.taobao.com/member/vst.htm?st=%s"%st, callback=self.parse_goods, encoding='gbk')

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
    
    def parse_goods(self, response):
        print "=="*10+" step 4 " + "="*10
        print "start parsing goods"
    
        