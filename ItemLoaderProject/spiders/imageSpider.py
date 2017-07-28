# -*- coding: utf-8 -*-
# TODO 参考的博客地址 http://www.jianshu.com/p/5b6fbf9245f8
# 这个爬虫主要是用来爬取网上的图片，并且下载到本地，写的比较好的地方时pipelines文件

from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.loader import ItemLoader, Identity
from ItemLoaderProject.items import ItemloaderprojectItem

class ImagespiderSpider(CrawlSpider):
    name = "imageSpider"
    # allowed_domains = ["meizitu.com"]
    start_urls = ['http://www.meizitu.com/a/list_1_1.html']

    def parse(self, response):
        selector = Selector(response)

        if (response.url).find('list') > 0:
            links = selector.xpath('//h3/a/@href').extract() # 爬取某个图片的子页面
        else:
            links = selector.xpath('//h2/a/@href').extract() # 爬取"美女分类"，逻辑是先爬完一个分类，才爬另一个分类

        for link in links:
            yield Request(link, callback=self.parse_item)
        # pass

        # 获得分页的链接，递归爬取下一页
        pages = selector.xpath('//div[@id="wp_page_numbers"]/ul/li/a/@href').extract()
        print('pages %s' % pages)
        if len(pages) > 2:
            page_link = pages[-2]  # 取得下一页的链接
            # page_link = page_link.replace('/a/', '')
            # url = 'http://www.meizitu.com/a/' + page_link
            # print url
            url = response.urljoin(page_link)
            yield Request(url, callback=self.parse)


    # 解析某个列表图片的子页面（看图页面）
    def parse_item(self, response):
        # 当Item在Spider中被收集之后，它将会被传递到Item Pipeline，一些组件会按照一定的顺序执行对Item的处理。
        l = ItemLoader(item=ItemloaderprojectItem(), response=response)
        l.add_xpath('name', '//h2/a/text()')
        l.add_xpath('tags', "//div[@id='maincontent']/div[@class='postmeta  clearfix']/div[@class='metaRight']/p")
        l.add_xpath('image_urls', "//div[@id='picture']/p/img/@src", Identity())
        l.add_value('url', response.url)

        # l.replace_value('url', 'www.baidu.com')
        # l.replace_xpath()
        # l.get_xpath()
        # l.add_xpath('price', '//p[@id="price"]', re='the price is (.*)')

        # Instead, you can create a nested loader with the footer selector and add values relative to the footer.
        # The functionality is the same but you avoid repeating the footer selector.
        # Example:
        # loader = ItemLoader(item=Item())
        # # load stuff not in the footer
        # footer_loader = loader.nested_xpath('//footer')
        # footer_loader.add_xpath('social', 'a[@class = "social"]/@href')
        # footer_loader.add_xpath('email', 'a[@class = "email"]/@href')
        # # no need to call footer_loader.load_item()
        # loader.load_item()

        return l.load_item()



# 内置的处理器

# Identity 啥也不做
# TakeFirst 返回第一个非空值，通常用作输出处理器
# Join 将结果连起来，默认使用空格’ ‘
# Compose 将函数链接起来形成管道流，产生最后的输出
# MapCompose 跟上面的Compose类似，区别在于内部结果在函数中的传递方式.它的输入值是可迭代的，首先将第一个函数依次作用于所有值，产生新的可迭代输入，作为第二个函数的输入，最后生成的结果连起来返回最终值，一般用在输入处理器中。
# SelectJmes 使用json路径来查询值并返回结果