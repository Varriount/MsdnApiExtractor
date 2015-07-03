# -*- coding: utf-8 -*-
import re
from code_scraper.items import ApiEntry
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from string import maketrans
from collections import OrderedDict

# Misc constants
strip_chars = u"\n\t\xa0"

# Domain constants
msdn_domain = "msdn.microsoft.com"
msdn_url = 'https://' + msdn_domain + '/en-us/library/windows/desktop'
msdn_filter = '[eE][nN]-[uU][sS]/library/windows'
deny_filter = [
    'login\.live\.com',
    'dev\.windows\.com',
    'community/add'
]

# XPath Constants
common_entry_xpath = "//div[@id='mainSection']/table/tr[{0}]"

table_xpath = "//div[@id='mainSection']//table"
code_xpath = ("//div[@id='code-snippet-1']"
              "//div[contains(@id,'CodeSnippetContainerCode')]"
              "/div/pre//text()")


def xpath_extract(resp, path):
    return (
        unicode(u''.join(resp.xpath(path).extract()))
        .strip(strip_chars)
        .replace(u"\xa0", u' ')
        .replace(u"\t", u' ')
        .replace(u"\x00", u'')
    )


class ApiSpider(CrawlSpider):
    name = "ApiSpider"
    allowed_domains = [msdn_domain]
    start_urls = (
        msdn_url + '/dn933214.aspx',
        msdn_url + '/ff818516.aspx',
    )
    rules = [
        Rule(
            LinkExtractor(allow=msdn_filter, deny=deny_filter),
            callback='parse_entry',
            process_links='process_links',
            follow=True
        )
    ]

    def process_links(self, links):
        for link in links:
            link.url = re.sub('\(v=.*?\)', '', link.url)
        return links

    def parse_entry(self, response):
        result = ApiEntry()

        # Set up result
        result['url'] = response.url
        result['code'] = xpath_extract(response, code_xpath)
        result['tables'] = []
        result['metadata'] = OrderedDict()

        # Get table data
        tables = response.xpath(table_xpath)
        for table in tables[0:-1]:
            rows = table.xpath("tr")
            table_header = xpath_extract(rows[:1], './/th//text()')

            entries = []
            for row in rows[1:]:
                entry = xpath_extract(row, 'td[1]//text()')
                entry = entry.replace("\n", " ")
                entries.append(entry)
            result['tables'].append((table_header, entries))

        # Get metadata
        location_list = tables[-1:].xpath("tr")
        for row in location_list:
            name = xpath_extract(row, 'th//text()').lower().replace("\n", "")
            value = xpath_extract(row, 'td//text()').replace("\n", "")
            result['metadata'][name] = value

        return result
