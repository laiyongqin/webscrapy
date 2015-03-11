# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

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
    brandName = scrapy.Field()
    shopName = scrapy.Field()
    wangwangUrl = scrapy.Field()
    companyName = scrapy.Field()
    shopType = scrapy.Field()
    shopLocation = scrapy.Field()
    tradeCount = scrapy.Field()
    # 营业执照链接
    ziZhaoUrl = scrapy.Field()