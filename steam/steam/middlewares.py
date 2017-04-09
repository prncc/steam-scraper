import os
from w3lib.url import url_query_cleaner

from scrapy.extensions.httpcache import FilesystemCacheStorage
from scrapy.utils.request import request_fingerprint


class SteamCacheStorage(FilesystemCacheStorage):
    def _get_request_path(self, spider, request):
        # For the purposes of caching we wish to discard the
        # unstable 'snr' query field.
        url = url_query_cleaner(request.url, ['snr'], remove=True)
        request = request.replace(url=url)
        key = request_fingerprint(request)
        return os.path.join(self.cachedir, spider.name, key[0:2], key)