#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import yaml
import sys
# sudo apt-get install python-pip
# sudo pip install websocket-client pyyaml

def getAvailablePlatforms(html, url):
    # document.getElementById('game_infobox').getElementsByTagName('tr')[1].getElementsByTagName('a')
    soup = BeautifulSoup(html)
    
    search_results = soup.find(id = 'game_infobox').find_all('tr')[1].find_all('a')
    result = {}

    # 'href' of the first item is the link for the platform ranking but not for the summary page
    item = search_results.pop(0)
    platform_name = item.string.encode('utf-8')
    result[platform_name] = url

    for item in search_results:
        platform_name = item.string.encode('utf-8')
        result[platform_name] = item.get('href').encode('utf-8')

    return result


def getURLsForRegion(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    search_results = soup.find(id = 'tabs').find_all('a')
    result = {}

    for item in search_results:
        region_name = item.string.encode('utf-8')
        if region_name not in ['Summary', 'Comments']:
            result[region_name] = item.get('href').encode('utf-8')

    return result


def filterByRegion(region_dict):
    if region_dict.has_key('France'):
        region_dict.pop('France')
    if region_dict.has_key('UK'):
        region_dict.pop('UK')
    if region_dict.has_key('Germany'):
        region_dict.pop('Germany')

    return region_dict


def getGameTitle(html):
    # document.getElementById('game_body').getElementsByTagName('a')[0].innerText
    soup = BeautifulSoup(html)
    game_title = soup.find(id = 'game_body').find_all('a')[0].string.encode('utf-8')

    return game_title


def getAnnualSummary(url, target_year):
    # document.getElementById('game_body').getElementsByTagName('div')[5].getElementsByTagName('td')
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    
    search_results = soup.find(id = 'game_body').find_all('div')
    annual_summary_item = None

    for item in search_results:
        if item.find('h2') and item.find('h2').string.find('Annual Summary') > 0:
            annual_summary_item = item

    if annual_summary_item:
        td_search_result = annual_summary_item.find_all('td')
        result = {}

        while len(td_search_result) > 0:
            year = int(td_search_result.pop(0).string)
            yearly = int(td_search_result.pop(0).string.replace(',', '').replace('N/A', '-1'))
            change = td_search_result.pop(0).string
            total = int(td_search_result.pop(0).string.replace(',', '').replace('N/A', '-1'))
            result[year] = {'yearly': yearly, 'total': total}

    if result.has_key(target_year):
        return result[target_year]

    return {'yearly': -1, 'total': -1}


def getAnnualChart(url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())

    search_results = soup.find('table', {'class' : 'chart'}).find_all('tr', recursive = False)[1:]
    result = []

    for item in search_results:
        tds = item.find_all('td', recursive = False);
        title = tds[1]('td')[1]
        url = title.find('a').get('href')
        result.append(url)

    return result


def main():
    url_list = getAnnualChart('http://www.vgchartz.com/yearly/2013/Global/')
    url_list += getAnnualChart('http://www.vgchartz.com/yearly/2013/Japan/')
    url_list += getAnnualChart('http://www.vgchartz.com/yearly/2013/USA/')
    url_list += getAnnualChart('http://www.vgchartz.com/yearly/2013/Europe/')
#    url_list = url_list[0:5]
    # get unique items in 'result'
    url_list = list(set(url_list))

    stat_result = {}

    platform_url_list = {}
    for url in url_list:
        html = urllib2.urlopen(url).read()
        game_title = getGameTitle(html)

        for platform_name, platform_url in getAvailablePlatforms(html, url).items():
            print platform_url
            platform_url_list[platform_url] = [game_title, platform_name]

    i = 0
    for platform_url, [game_title, platform_name] in platform_url_list.items():
        i += 1
        for region_name, region_url in filterByRegion(getURLsForRegion(platform_url)).items():
            print region_url
            summary = getAnnualSummary(region_url, 2013)
            print "%s/%s: %s (%s / %s) : %s" % (i, len(platform_url_list), game_title, platform_name, region_name, summary)

            stat_result[game_title][platform_name][region_name] = summary;

    outfile = open('output.yml', 'wb')
    yaml.dump(stat_result, outfile)
    outfile.close()

if __name__ == "__main__":
    main()
