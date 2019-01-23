# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

from ArticalSpider.items import JobBoleArticleItem
from ArticalSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    # start_urls = ['http://blog.jobbole.com/all-posts/']
    start_urls = ['http://blog.jobbole.com/all-posts/page/563/']

    def parse(self, response):
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first('')
            image_url = parse.urljoin(response.url, image_url)
            post_url = post_node.css('::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url}, callback=self.parse_detail)

        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    def parse_detail(self, response):
        artical_item = JobBoleArticleItem()
        
        front_image_url = response.meta.get('front_image_url', '')
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·', '').strip()
        praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first('')
        fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        match_re = re.match('.*?(\d+).*', fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        match_re = re.match('.*?(\d+).*', comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.xpath('//div[@class="entry"]').extract()[0]

        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)

        artical_item['url_object_id'] = get_md5(response.url)
        artical_item['title'] = title
        artical_item['url'] = response.url
        artical_item['create_date'] = create_date
        artical_item['front_image_url'] = [front_image_url]
        artical_item['praise_nums'] = praise_nums
        artical_item['comment_nums'] = comment_nums
        artical_item['fav_nums'] = fav_nums
        artical_item['tags'] = tags
        artical_item['content'] = content
        
        yield artical_item
