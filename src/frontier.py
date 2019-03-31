import hashlib
from collections import deque
from urllib.parse import urlparse, urlsplit, quote, unquote
from os.path import splitext, basename, normpath


class Frontier:
    def __init__(self, seed):
        self._frontier = deque()
        self._seed = seed
        self._history = {}

    def _base_url(self, url):
        split_url = urlsplit(url)
        return "://".join([split_url.scheme, split_url.netloc])

    def _get_url_hash(self, url):
        m = hashlib.sha1()
        m.update(url.encode('utf-8'))
        return m.hexdigest()

    def _norm_url(self, url):
        url = urlparse(url)

        # change https to http
        url = url._replace(scheme=url.scheme.replace("https", "http"))

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

    def add_url(self, url, page_id):
        url = self._norm_url(url)
        base = self._base_url(url)
        if base in self._seed:
            hash_text = self._get_url_hash(url)
            if hash_text not in self._history:
                self._history[hash_text] = url
                self._frontier.append((url, page_id,))

    def add_urls(self, urls, page_id):
        for url in urls:
            self.add_url(url, page_id)

    def get_next(self):
        return self._frontier.popleft()

    def has_urls(self):
        return len(self._frontier) > 0

    def frontier_content(self):
        return self._frontier
