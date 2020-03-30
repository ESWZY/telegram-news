# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import urllib.parse


def keep_link(text, url):
    """Remove tags except <a></a>. Otherwise, telegram api will not parse"""

    soup = BeautifulSoup(text, 'lxml')
    # print(text)
    # print(soup.select('img, a'))

    # No link here, return directlly
    if soup.select('a') == []:
        return soup.getText()

    # Find link(s)
    else:

        # Copy from original text
        cp = str(soup)

        # The target string
        result = ""

        # Remove other tags, except <a>
        for link in soup.select('a, img'):

            # Split the text by <a> tag
            other = str(cp).split(str(link))

            # Get one link url
            content = link.get_text()
            url = link.get('href')

            # Get plain text and concatenate with link
            result += BeautifulSoup(other[0], 'lxml').getText()
            if url:
                result += '<a href=\"' + url + '\" >' + str(content) + '</a>'

            # Remove the processed text from processing string
            cp = str(cp).replace(str(other[0]) + str(link), "")

        # Return processed text and the plain text behind
        return result + BeautifulSoup(cp, 'lxml').getText()


def str_url_encode(l):
    return urllib.parse.quote(l)


print("DELETED!!")