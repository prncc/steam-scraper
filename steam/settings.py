from smart_getenv import getenv

BOT_NAME = 'steam'

SPIDER_MODULES = ['steam.spiders']
NEWSPIDER_MODULE = 'steam.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'steam.middlewares.CircumventAgeCheckMiddleware': 600,
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0

DUPEFILTER_CLASS = 'steam.middlewares.SteamDupeFilter'

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0  # Never expire.
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [301, 302, 303, 306, 307, 308]
HTTPCACHE_STORAGE = 'steam.middlewares.SteamCacheStorage'

AWS_ACCESS_KEY_ID = getenv('AWS_ACCESS_KEY_ID', type=str, default=None)
AWS_SECRET_ACCESS_KEY = getenv('AWS_SECRET_ACCESS_KEY', type=str, default=None)
