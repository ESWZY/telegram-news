# -*- coding: UTF-8 -*-

try:
    import urlparse
    from urllib import urlencode
except ModuleNotFoundError:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

from bs4 import BeautifulSoup


def keep_img(text, url):
    soup = BeautifulSoup(text, 'html.parser')
    # print(text)

    # No image here, return directly
    if not soup.select('img'):
        return soup.getText()

    # Find image(s)
    else:
        # Copy from original text
        cp = str(soup)

        # The target string
        result = ""

        # Remove other tags, except <a>
        for img in soup.select('img'):

            # Split the text by <img> tag
            other = str(cp).split(str(img))

            # Get the image url
            img_link = img.get('src')

            # Get plain text and concatenate with link
            result += BeautifulSoup(other[0], 'html.parser').getText().strip()
            if img_link:
                # If the image link is a relative path
                img_link = get_full_link(img_link, url)

                # Embed the image as a link
                result += '<a href=\"' + img_link + '\">' + '[Media]' + '</a>'

            # Remove the processed text from processing string
            cp = str(cp).replace(str(other[0]) + str(img), "")

        # Return processed text and the plain text behind
        return result + BeautifulSoup(cp, 'html.parser').getText()


def keep_link(text, url):
    """Remove tags except <a></a>. Otherwise, telegram api will not parse"""

    soup = BeautifulSoup(text, 'html.parser')
    # print(text)
    # print(soup.select('img, a'))

    # No link here, return directly
    if not soup.select('a'):
        return keep_img(text, url)

    # Find link(s)
    else:

        # Copy from original text
        cp = str(soup)

        # The target string
        result = ""

        # Remove other tags, except <a>
        for link in soup.select('a'):

            # Split the text by <a> tag
            other = str(cp).split(str(link))

            # Get the link url
            content = link.get_text()
            link_url = link.get('href')

            # Get plain text and concatenate with link
            result += keep_img(other[0], url)
            if url:
                result += '<a href=\"' + link_url + '\">' + str(content) + '</a>'

            # Remove the processed text from processing string
            cp = str(cp).replace(str(other[0]) + str(link), "")

        # Return processed text and the plain text behind
        return result + keep_img(cp, url)


def is_single_media(text):
    soup = BeautifulSoup(text, 'html.parser')

    # No <a> tag here, return directly
    if not soup.select('a'):
        return False
    else:
        anchor = soup.select('a')[0]
        # print(anchor)

        if anchor.getText() == '[Media]':
            if text.replace(str(anchor), '') == '':
                return True
    return False


def str_url_encode(l):
    return urlparse.quote(l)


def get_full_link(link, base_url):
    """Parse the relative link to absolute link."""
    return urlparse.urljoin(base_url, link)


def add_parameters_into_url(url, parameters):
    """The url might already have GET parameters or not. parameters is a dict"""
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(parameters)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)


def is_length_immunity(item):
    if item['title'][:4] == '综合消息':
        return True
    return False


print("DELETED!!")