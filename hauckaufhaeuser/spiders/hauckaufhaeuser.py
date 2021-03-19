import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hauckaufhaeuser.items import Article


class HauckaufhaeuserSpider(scrapy.Spider):
    name = 'hauckaufhaeuser'
    start_urls = ["https://www.hauck-aufhaeuser.com/?type=24219&L=0&cid=83&starttime=&endtime=&offset=0&tx_wvhua_news%5Baction%5D=more"]
    page = 0

    def parse(self, response):
        articles = response.xpath('//div[@class="timeline-element"]')
        for article in articles:
            link = article.xpath('.//a[@class="more"]/@href').get()
            date = article.xpath('.//div[@class="date"]/text()[2]').get()
            if date:
                date = date.split()[-1]
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        if articles:
            self.page += 1
            next_page = f"https://www.hauck-aufhaeuser.com/?type=24219&L=0&cid=83&starttime=&endtime=&offset={self.page}&tx_wvhua_news%5Baction%5D=more"
            yield response.follow(next_page, self.parse)


    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="ce-bodytext"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
