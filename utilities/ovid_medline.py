from __future__ import unicode_literals
from bs4 import BeautifulSoup
from downloader import Downloader
from redirect import setUrl

D = Downloader()
U = setUrl()


class ovidRef:
    def __init__(self, downloader=D, url=U):
        self.downloader = downloader
        self.url_modifier = url

    def __call__(self, uri):
        updated_url = self.ovidUrl(uri)
        references = self.extractInfo(self.downloader(updated_url))
        return references

    def ovidUrl(self, uri):
        ref_url = self.url_modifier(uri)
        return ref_url

    def extractInfo(self, html):
        keywords = []
        flag = False

        soup = BeautifulSoup(html, 'html.parser')
        print(soup.prettify())
        for keyword in soup.find_all('th'):
            if keyword != None:
                if keyword.get_text().lower() == "author keywords:":
                    keywords.append(keyword.find_next_sibling().get_text())
                    flag = True
        if flag != True:
            for keyword in soup.find_all('p', class_=['fulltext-TEXT' 'fulltext-INDENT']):
                if keyword != None:
                    if keyword.get_text().lower().startswith("author keywords:"):
                        keywords.append(keyword.get_text())

        index_info = ''.join(keywords)
        index_info = index_info.encode('utf-8')

        return index_info
