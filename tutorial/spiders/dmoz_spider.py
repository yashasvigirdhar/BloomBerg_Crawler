from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from tutorial.items import DmozItem
from scrapy.http import Request
import nltk
from pymongo import *

class DmozSpider(CrawlSpider):
	name = "dmoz"
	allowed_domains = ["bloomberg.com"]
	start_urls = ["http://www.bloomberg.com/"]
	fp = open('indi.txt','w')
	fp2 = open('content.txt','w')
	#items = []
	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		fp = open('b.txt','w')
		body = hxs.select('//body')
		div = body.select('//div[@class="nav_container"]')
		lis = div.select('//ul[@class="drop_nav"]/li')
		site = "http://www.bloomberg.com"
		lis = lis[1:]
		items = []
		for l in lis:
			k = l.select('.//a');
			mainurl = site + k[0].select('@href').extract()[0]
			if len(k)==1:
				fp.write(mainurl+'\n')
			k = k[1:]
			for j in k:
				url = j.select('@href').extract()[0]
				if not url.startswith("http"):
					url = site + url;
				fp.write(url+'\n');
				yield Request(url=url, meta={'url': url}, callback=self.parse_page)
				#items.append(res)
		fp.close()
		#yield items
	
	def parse_page(self,response):
		site = "http://www.bloomberg.com"
		hxs = HtmlXPathSelector(response)
		pagetitle = hxs.select('//title/text()').extract()[0];
		fp = open('indi.txt','a')
		fp.write(pagetitle+'\n\n')
		articles = hxs.select('//a[@data-type="Story"]')
		items = []
		for article in articles:
			title = article.select('text()').extract()
			if len(title)==0:
				continue;
			title = title[0]
			title = title.encode('utf8')
			url = site + article.select('@href').extract()[0]
			url = url.encode('utf8')
			fp.write(title+'\n'+url+'\n\n')
			yield Request(url=url, meta={'url': url}, callback=self.parse_news)
			#print response
			#items.append(response)
		fp.close()
		#yield items

	def parse_news(self,response):
		item = DmozItem()
		#global items
		#print url
		client = MongoClient()
		hxs = HtmlXPathSelector(response)
		fp = open('content.txt','a')
		title = hxs.select('//title/text()').extract()[0]
		fp.write(title.encode('utf8')+'\n\n')
		item['title'] = title
		text = hxs.select('//div[@class="entry_content"]/p').extract()
		content = ""
		if len(text) > 0:
			for t in text:
				tt = nltk.clean_html(t)
				tt = tt.encode('utf8')
				content = content + tt
				#item['content'] = tt.encode('utf8')
				fp.write(tt+'\n')
			fp.write('\n\nend of article\n\n')
		client.test.test_c.update({"title" : title},{"title" : title,"content" : content},True)
		#items.append(item)
		#return item

