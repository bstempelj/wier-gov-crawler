import hashlib
from collections import deque

class Frontier:
    def __init__(self):
        self._frontier = deque()
        self._history = {}

    def add_url(self, url):
        m = hashlib.sha1()
        m.update(url.encode('utf-8'))
        hash_text = m.hexdigest()
        if hash_text not in self._history:
            self._history[hash_text] = url
            self._frontier.append(url)

    def add_urls(self, urls):
        for url in urls:
            self.add_url(url)

    def get_next(self):
        return self._frontier.pop()

    def has_urls(self):
        return len(self._frontier) > 0
