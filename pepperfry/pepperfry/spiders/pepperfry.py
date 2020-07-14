import scrapy
import os
import requests

class pepperfrySpider(scrapy.Spider):
    name = "pepperfry"
    BASE_DIR = './Pepperfry_data/'

    def start_requests(self):
        BASE_URL = "https://www.pepperfry.com/site_product/search?q="

        items = ["two seater sofa","book case","bench","coffee table","dining set"]

        urls=[]
        dir_names = []

        for item in items:
            dir_name = '-'.join(item.split(' '))
            query_string = '+'.join(item.split(' '))
            urls.append(BASE_URL + query_string)
            dir_names.append(dir_name)
            
            dir_path = self.BASE_DIR + dir_name
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
        for i,url in enumerate(urls):
            resp = scrapy.Request(url=url,callback = self.parse)
            resp.meta['dir_name'] = dir_names[i]
            yield resp

    def parse(self,response):
        product_urls = response.xpath('//div/div/div/h2/a/@href').extract()

        # Below lines are used for running shell for those urls that are also authenticated like pepperfry
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        for i,url in enumerate(product_urls):
            if i<10:
                resp = scrapy.Request(url=url,callback = self.parse_response)
                resp.meta['dir_name'] = response.meta['dir_name']
                yield resp

    def parse_response(self,response):
        image_urls = response.xpath('//li[@class="vipImage__thumb-each noClickSlide"]/a/@data-img').extract()
        item_title = response.xpath('//div/div/div/h1/text()').extract()[0]
        
        CATEGORY_NAME = response.meta['dir_name']
        ITEM_DIR_URL = os.path.join(self.BASE_DIR,os.path.join(CATEGORY_NAME,item_title))
        
        if not os.path.exists(ITEM_DIR_URL):
            os.makedirs(ITEM_DIR_URL)
            
        for idx,image in enumerate(image_urls):
            if idx<5:
                with open(os.path.join(ITEM_DIR_URL,'img-{}.jpg'.format(idx)),'wb') as f:
                    f.write(requests.get(image).content)
