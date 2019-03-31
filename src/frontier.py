import hashlib
from collections import deque
from urllib.parse import urlparse, quote, unquote
from os.path import splitext, basename, normpath


class Frontier:
    def __init__(self):
        self._frontier = deque()
        self._history = {}
        self._max_urls = -1

    def _norm_url(self, url):
        url = urlparse(url)

        # lowercase network part and remove www
        url = url._replace(netloc=url.netloc.lower().replace("www.", ""))

        # unquote and quote path
        url = url._replace(path=unquote(url.path))
        url = url._replace(path=quote(url.path))

        # normalize path
        if url.path != "":
            url = url._replace(path=normpath(url.path).replace("\\", "/"))

        # remove port from url
        port = url.netloc.find(":")
        if port != -1:
            no_port = url.netloc[:port]
            url = url._replace(netloc=no_port)

        # path/file and file extension
        path, ext = splitext(url.path)

        # add trailing slash to netloc
        if path == "":
            url = url._replace(netloc=url.netloc + "/")
        # add trailing slash to path
        elif ext == "" and not path.endswith("/"):
            url = url._replace(path=url.path + "/")
        # remove index.html
        elif ext == ".html" and path.endswith("index"):
            url = url._replace(path="/")

        return "{}://{}{}".format(url.scheme, url.netloc, url.path)

    def add_url(self, url):
        url = self._norm_url(url)
        if not self.max_reached() or self._max_urls == -1:
            self._max_urls -= 1
            hash_text = self._get_url_hash(url)
            if hash_text not in self._history:
                self._history[hash_text] = url
                self._frontier.append(url)

    def add_urls(self, urls):
        for url in urls:

            self.add_url(url)

    def get_next(self):
        return self._frontier.popleft()

    def has_urls(self):
        return len(self._frontier) > 0

    def frontier_content(self):
        return self._frontier

    def max_reached(self):
        return self._max_urls == 0

    def _get_url_hash(self, url):
        m = hashlib.sha1()
        m.update(url.encode('utf-8'))
        return m.hexdigest()
