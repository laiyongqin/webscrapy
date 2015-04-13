# -*- coding: utf-8 -*-

import re
import scrapy
import json
import traceback
import sys
from scrapy import Request
from scrapys.items import Category

class TmallCategorySpider(scrapy.Spider):
    name = 'tmallcategory'
    download_delay = 1
    start_urls = ['http://www.taobao.com']
    ocat = list()               
    pcatId = set()
    f2_1 = open("propIds.txt", "a+")
    f2 = open("props2.txt", "a")
    f3 = open("propValues2.txt", "a")
    def __init__(self, category=None, *args, **kwargs):
        f = open("20150319.json", "r")
        text = f.read()
        if len(text) > 0:
            ocat1 = json.loads(text)
            for cat in ocat1:
                self.ocat.append(cat)
                
        print "reading prop Ids"
        props = self.f2_1.readlines()
        for prop in props:
            self.pcatId.add(int(prop))
            
    def start_requests(self):
        print "=="*10+" step 1 " + "="*10
        #yield Request("http://api.taobao.com/apitools/apiPropTools.htm", callback=self.parse_page)
        print len(self.pcatId)
        for cat in self.ocat:
            cid = cat["cid"]
            is_parent = cat["is_parent"]
            if is_parent == False and cid not in self.pcatId:
                url = "http://api.taobao.com/apitools/ajax_props.do?act=props&cid=%s&restBool=false"%cid
                yield Request(url, callback=self.parse_attribute, meta=dict(pcid=cid))
            else:
                print "already crapyed or not parent"

    def parse_page(self, response):
        print "=="*10+" step 2 " + "="*10
        text = response.body.decode("utf-8", 'ignore')
        #print text
        jsonText = re.search("var cid1_api = '0\|(.*)\|0'", text).group(1)
        jsonText = jsonText.replace("\\\"", "\"").replace("\\\\\\", "")
        result = json.loads(jsonText)
        arr = result["itemcats_get_response"]["item_cats"]["item_cat"]
        for cat in arr:
            category = Category()
            isParent = cat["is_parent"]
            name = cat["name"]
            cid = cat["cid"]
            #print "cid:" + str(cid)
            category["cid"] = cat["cid"]
            category["is_parent"] = cat["is_parent"]
            category["name"] = cat["name"]
            category["parent_cid"] = cat["parent_cid"]
            category["status"] = cat["status"]
            
            if isParent == True:
                url = "http://api.taobao.com/apitools/ajax_props.do?cid=%s&act=childCid&restBool=false"%cid
                yield Request(url, callback=self.parse_category, meta=dict(pcat=category))
                yield category
            else:
                yield category
                #url = "http://api.taobao.com/apitools/ajax_props.do?act=props&cid=%s&restBool=false"%cid
                #yield Request(url, callback=self.parse_attribute)

    def parse_category(self, response):
        print "=="*10+" step 3 " + "="*10
        text = response.body.decode("utf-8", 'ignore')
        #pcat = response.meta["pcat"]
        try:
            result = json.loads(text, "utf-8")
            print "json no error found"
            #yield pcat
            #print "result:" + str(result)
            arr = result["itemcats_get_response"]["item_cats"]["item_cat"]
            for cat in arr:
                category = Category()
                cid = cat["cid"]
                parent_cid = cat["parent_cid"]
                #print "parent_cid:%s"%parent_cid + " cid:%s"%cid
                isParent = cat["is_parent"]
                category["cid"] = cat["cid"]
                category["is_parent"] = cat["is_parent"]
                category["name"] = cat["name"].encode("utf8", 'ignore')
                category["parent_cid"] = cat["parent_cid"]
                category["status"] = cat["status"]
                if isParent == True:
                    url = "http://api.taobao.com/apitools/ajax_props.do?cid=%s&act=childCid&restBool=false"%cid
                    #yield Request(url, callback=self.parse_category, meta=dict(pcat=self.category))
                    yield category
                else:
                    yield category
                    # url = "http://api.taobao.com/apitools/ajax_props.do?act=props&cid=%s&restBool=false"%cid
                    #yield Request(url, callback=self.parse_attribute, meta=dict(cid=cid,proxy="http://122.96.59.106:80"))
        except Exception as err:
            print "Printing only the traceback above the current stack frame"
            print "".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]))
            print
            print "Printing the full traceback as if we had not caught it here..."
            print self.format_exception(err)

    def parse_attribute(self, response):
        print "=="*10+" step 4 " + "="*10
        text = response.body#.decode("utf-8", 'ignore')
        pcid = response.meta["pcid"]
        rlen = len(text)

        print "response length:" + str(rlen)
        if rlen == 28:
            print "please stop, blocked"
            return

        m = re.search("itemprops_get_response", text)
        if not m:
            return

        print "write parent cid to cache file"
        self.f2_1.write(str(pcid) + "\n")
        if rlen == 94:
            print "not valid result found, write empty content"
            self.f2.write('{"cid": %s, "value": []},\n'%(pcid))
            return
            

        m1 = re.search('var props=.*"item_prop"\:(.*)\}\}\};[^$]', text)#.group(1)
        m2 = re.search("var propvalues=.*\"prop_value\"\:\[(.*)\]\}\}\};$", text)#.group(1)
        if m1:
            print "write props"
            self.f2.write('{"cid": %s, "value": %s},\n'%(pcid, m1.group(1)))
        if m2:
            print "write prop values"
            self.f3.write(m2.group(1) + ",\n")
#         print m1
#         print m2
#         propResponse = json.loads(m1)["itemprops_get_response"].get("item_props")
#         valueResponse = json.loads(m2)["itempropvalues_get_response"].get("prop_values")
#         if propResponse != None:
#             print "start transfer props"
#             props = propResponse["item_prop"]
#             print "write length props: %d"%len(props)
#             for prop in props:
#                 child_template = prop.get("child_template")
#                 name = prop.get("name")#.decode("utf-8", 'ignore')
#                 print name
#                 if child_template == None:
#                     child_template = ""
#                 self.f2.write('{"pid":%s,"child_template":%s, "name":%s,'%(pcid, child_template, name.decode("utf8", 'ignore')) + ',"is_color_prop":%(is_color_prop)s,"is_enum_prop":%(is_enum_prop)s,"is_input_prop":%(is_input_prop)s,"is_item_prop":%(is_item_prop)s,"is_key_prop":%(is_key_prop)s,"is_sale_prop":%(is_sale_prop)s,"multi":%(multi)s,"must":%(must)s,"parent_pid":%(parent_pid)d,"parent_vid":%(parent_vid)d,"pid":%(pid)d,"sort_order":%(sort_order)d,"status":%(status)s}\n'%prop)
#         if valueResponse != None:
#             pvs = valueResponse["prop_value"]
#             print "write length value: %d"%len(pvs)
#             for pv in pvs:
#                 cid = pv["cid"]
#                 name = pv["name"]
#                 name_alias = pv["name_alias"]
#                 pid = pv["pid"]
#                 prop_name = pv["prop_name"]
#                 sort_order = pv["sort_order"]
#                 status = pv["status"]
#                 vid = pv["vid"]
#                 self.f3.write('{"cid":%d,"name":%s,"name_alias":%s,"pid":%d,"prop_name":%s,"sort_order":%d,"status":%s,"vid":%d}\n'%(cid, name, name_alias, pid, prop_name, sort_order, status, vid))

    def close(self, reason):
        print "=="*10+" step 5 " + "="*10
        #self.f1.close()
        # f1 = open("category.txt", "w+")
        # f2 = open("props.txt", "w+")
        # f3 = open("propValues.txt", "w+")
        # f1.write(self.category)
        # f2.write(self.props)
        # f3.write(self.propValues)
        # f1.close()
        self.f2.close()
        self.f3.close()
        self.f2_1.close()

    def format_exception(self, e):
        exception_list = traceback.format_stack()
        exception_list = exception_list[:-2]
        exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
        exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

        exception_str = "Traceback (most recent call last):\n"
        exception_str += "".join(exception_list)
        # Removing the last \n
        exception_str = exception_str[:-1]

        return exception_str


        