import requests
from bs4 import BeautifulSoup


def url_to_bs(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'}
    response = requests.get(url, headers=headers)

    return BeautifulSoup(response.text, "html.parser")


def bs_to_info(soup):
    block = soup.select_one('.col-sm-8')

    result = {}
    try:
        position = soup.select_one('.author-dolj').text
        if position:
            result.update({'position': position.strip()})
    except AttributeError:
        pass

    try:
        office = soup.select_one('.block-address').text.split(',')[-1]
        if office:
            result.update({'office': office.strip()})
    except AttributeError:
        pass

    try:
        surname, name, middle_name = soup.select_one(
            '.author-name').text.split(' ')
        if surname:
            result.update({'surname': surname.strip()})
        if name:
            result.update({'name': name.strip()})
        if middle_name:
            result.update({'middle_name': middle_name.strip()})
    except AttributeError:
        pass
    try:
        email = soup.select_one(
            'div.block-email:nth-child(1)').text
        if email:
            result.update({'email': email.strip()})
    except AttributeError:
        pass

    try:
        phone = soup.select_one(
            'div.col-md-12:nth-child(2) > div:nth-child(1)').text
        if phone:
            result.update({'phone': phone.strip()})
    except AttributeError:
        pass

    return result


def url_to_info(relative_url):
    soup = url_to_bs('https://www.dvfu.ru' + relative_url)
    rectore_info = bs_to_info(soup)

    return rectore_info


def parser():
    main_url = 'https://www.dvfu.ru/about/rectorate/scheme/'
    soup = url_to_bs(main_url)

    rectore_url = soup.select_one(
        '.secondline > td:nth-child(2) > table:nth-child(1) > '
        'tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > a:nth-child(1)'
    ).get('href')
    prorector_urls = [prorector.get('href') for prorector in soup.select_one(
        'td.node-container:nth-child(1) > table:nth-child(1) > '
        'tbody:nth-child(1)'
    ).find_all('a')]

    data = [url_to_info(rectore_url), ]
    for prorector_url in prorector_urls:
        data.append(url_to_info(prorector_url))

    for i, doc in enumerate(data):
        data[i].update({'const': False})

    return data


if __name__ == "__main__":
    print(parser())
