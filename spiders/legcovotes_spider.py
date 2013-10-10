from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XmlXPathSelector

from selenium import selenium

from scrapy import log
import time

from scrapy.http import Request
import urlparse

#from DFORM.items import LegcoVotes
# item defined here but ideally should be imported with the line above
from scrapy.item import Item, Field

class LegcoVotes(Item):
    company = Field()

class LegcoVotesSpider(CrawlSpider):
    name = "LegcoVotingRecords"
    allowed_domains = ["http://www.legco.gov.hk"]
    start_urls = [
        "http://www.legco.gov.hk/general/english/counmtg/yr12-16/mtg_1213.htm"
    ]

    #rules = (
        #Rule(
        #    SgmlLinkExtractor(restrict_xpaths=('//*[@id="_content_"]/div[2]/table/tbody/tr[3]/td[2]/div/table/tbody/tr[3]/td[3]/span/a[2]')),
        #    callback='parse_voting_record',
        #    #follow= True   # no need to apply the link rules for formd pages
        #),
        # Nex pages to scrape:
        # fetch the link with text '[NEXT]' in the first <center> tag (above the main <table>)
        # center[2] would select the [NEXT] link below the table
        #Rule(
        #    SgmlLinkExtractor(restrict_xpaths=('/html/body/div/center[1]/a[contains(., "[NEXT]")]')),
        #    follow= True
        #),
    #)

    def __init__(self):
        CrawlSpider.__init__(self)
        self.verificationErrors = [] 
        self.selenium = selenium("localhost", 4444, "*chrome", "http://www.legco.gov.hk/general/english/counmtg/yr12-16/mtg_1213.htm")
        self.selenium.start()

    def __del__(self):
        self.selenium.stop()
        print self.verificationErrors
        CrawlSpider.__del__(self)

    def parse(self, response):
        #hxs = HtmlXPathSelector(response)
        #sites = hxs.select('a/[contains(text(),"XML")]/@href').extract()
        sel = self.selenium
        sel.open(response.url)

        #Wait for javscript to load in Selenium
        time.sleep(2.5)

        sites = sel.get_attribute('//a[contains(text(),"(XML)")]/@href')
        for site in sites:
            url=urlparse.urljoin("http://www.legco.gov.hk/", site)
            log.msg("XML: "+url, level=log.DEBUG)
            yield Request(url, callback=self.parse_xml_document)
            

    def parse_xml_document(self, response):
        xxs = XmlXPathSelector(response)
        item = LegcoVotes()
        item["member_vote"] = xxs.select('//individual-votes/member/vote/text()').extract()[0]
        # XPaths to fix
        #item['company'] = site.select('//*[@id="collapsible1"]/div[1]/div[2]/div[2]/span[2]/text()').extract()
        #item['filling_date'] = site.select('//*[@id="collapsible40"]/div[1]/div[2]/div[5]/span[2]/text()').extract()
        #item['types_of_securities'] = site.select('//*[@id="collapsible37"]/div[1]/div[2]/div[1]/span[2]/text()').extract()
        #item['offering_amount'] = site.select('//*[@id="collapsible39"]/div[1]/div[2]/div[1]/span[2]/text()').extract()
        #item['sold_amount'] = site.select('//*[@id="collapsible39"]/div[1]/div[2]/div[2]/span[2]/text()').extract()
        #item['remaining'] = site.select('//*[@id="collapsible39"]/div[1]/div[2]/div[3]/span[2]/text()').extract()
        #item['investors_accredited'] = site.select('//*[@id="collapsible40"]/div[1]/div[2]/div[2]/span[2]/text()').extract()
        #item['investors_non_accredited'] = site.select('//*[@id="collapsible40"]/div[1]/div[2]/div[1]/span[2]/text()').extract()

        return item