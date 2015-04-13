# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class ScrapysItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ProdItem(scrapy.Item):
    category = scrapy.Field()
    attrs = scrapy.Field()
    skus = scrapy.Field()

class TmallBrand(scrapy.Item):
    # 主营业务
    shopUrl = scrapy.Field()
    category = scrapy.Field()
    #brandId = scrapy.Field()
    brandName = scrapy.Field()
    shopName = scrapy.Field()
    #wangwangUrl = scrapy.Field()
    companyName = scrapy.Field()
    shopType = scrapy.Field()
    shopProvince = scrapy.Field()
    shopCity = scrapy.Field()
    tradeCount = scrapy.Field()
    # 营业执照链接
    ziZhaoUrl = scrapy.Field()

class Category(scrapy.Item):
    cid = scrapy.Field()
    is_parent = scrapy.Field()
    name = scrapy.Field()
    parent_cid = scrapy.Field()
    status = scrapy.Field()       
    
class ItemProps(scrapy.Item):
    child_template = Field()
    is_color_prop = Field()
    is_enum_prop = Field()
    is_input_prop = Field()
    is_item_prop = Field()
    is_key_prop = Field()
    is_sale_prop = Field()
    multi = Field()
    must = Field()
    name = Field()
    parent_pid = Field()
    cid = Field() # Add by Owen
    parent_vid = Field()
    pid = Field()
    sort_order = Field()
    status = Field()

class PropValue(scrapy.Item):
    cid = Field()
    name = Field()
    name_alias = Field()
    pid = Field()
    prop_name = Field()
    sort_order = Field()
    status = Field()
    vid = Field()