from html.parser import HTMLParser
from urllib.parse import urlparse, urlunparse
import os
import re
import requests

from config import *


__all__ = ['get_images']


def download_file(url, local_path):
    r = requests.get(url, stream=True)
    with open(local_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)


def build_url(base, url):
    if url.startswith('//') or url.startswith('http'):
        return url
    scheme, host, path, params, query, fragment = urlparse(base)
    return urlunparse((scheme, host, url, '', '', ''))


class Crawler(HTMLParser):
    tag = None
    h1 = None
    images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.tag = tag
            self.h1 = ''
        elif tag == 'img' and ('class', 'pic') in attrs:
            if self.h1 is None:
                return

            sched_name = self.h1.strip()
            atb = dict(attrs)
            remote_fname = atb['src'].split('/')[-1]
            fname = os.path.join(self.img_dir, re.sub(r'[^a-zA-Z0-9]+', '-', sched_name) + '-' + remote_fname)
            download_file(build_url(CORE['schedule_url'], atb['src']), fname)

            self.images.append({
                'name': sched_name,
                'file': fname,
            })

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.tag = None

    def handle_data(self, data):
        if self.tag == 'h1':
            self.h1 += data


def get_images(img_dir=''):
    r = requests.get(CORE['schedule_url'])

    crawler = Crawler()
    crawler.img_dir = img_dir
    crawler.feed(r.content.decode())

    return crawler.images


if __name__ == '__main__':
    # FIXME: Rudimentary manual testing
    import sys
    img = get_images(img_dir=sys.argv[1])
    print(img)
