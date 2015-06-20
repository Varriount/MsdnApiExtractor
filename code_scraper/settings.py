# -*- coding: utf-8 -*-

# Scrapy settings for code_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

AUTOTHROTTLE_ENABLED = 1
BOT_NAME = 'code_scraper'
COOKIES_ENABLED = False
DEPTH_LIMIT = 10
DOWNLOAD_DELAY = 2
ITEM_PIPELINES = {
    'code_scraper.pipelines.ApiExportPipeline': 1
}
NEWSPIDER_MODULE = 'code_scraper.spiders'
RETRY_ENABLED = True
ROBOTSTXT_OBEY = True
SPIDER_MODULES = ['code_scraper.spiders']
USER_AGENT = ('Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36')
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
# Crawl responsibly by identifying yourself (and your website) on the
# user-agent
