#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml
import sys

def getRegionList(stat_result):
    return ['Global', 'USA', 'Europe', 'Japan']

    regions = {}
    for title, stat in stat_result.items():
        for platform_name, platform_value in stat.items():
            if isinstance(platform_value, dict):
                for region_name, region_value in platform_value.items():
                    regions[region_name] = 1

    return regions.keys()


def getPlatformList(stat_result):
    platforms = {}
    for title, stat in stat_result.items():
        for platform_name, platform_value in stat.items():
            if isinstance(platform_value, dict):
                platforms[platform_name] = 1

    return platforms.keys()

def addStatOverPlatform(stat_result):
    for title, stat in stat_result.items():
        yearly_over_platform = 0
        total_over_platform = 0
        for platform_name, platform_value in stat.items():
            if isinstance(platform_value, dict):
                for region_name, region_value in platform_value.items():
                    if region_name == 'Global':
                        yearly_over_platform += region_value['yearly']
                        total_over_platform += region_value['total']
        
        stat_result[title]['yearly_over_platform'] = yearly_over_platform
        stat_result[title]['total_over_platform'] = total_over_platform

    return stat_result


def main():
    infile = open('output.yml', 'rb')
    stat_result = yaml.load(infile)
    infile.close()

    outfile = open('output.csv', 'wb')

    region_list = getRegionList(stat_result)
    platform_list = getPlatformList(stat_result)

    stat_result = addStatOverPlatform(stat_result)

    line = '"Title","Yearly","Total"'
    for platform_name in platform_list:
        line += ',"' + platform_name + '"'
    for region_name in region_list:
        if region_name != 'Global':
            line += ',"' + region_name + '"'
    for platform_name in platform_list:
        for region_name in region_list:
            line += ',"' + platform_name + '/' + region_name + '/total"'
            line += ',"' + platform_name + '/' + region_name + '/yearly"'

    line += '\n'
    outfile.write(line)

    for title, stat in sorted(stat_result.items(), key = lambda x:x[1]['yearly_over_platform'], reverse = True):
        yearly_total = stat['yearly_over_platform']
        line = '"%s",%s,%s' % (title, stat['yearly_over_platform'], stat['total_over_platform'])

        for platform_name in platform_list:
            platform_total = 0
            if stat.has_key(platform_name):
                for region_name, region_value in stat[platform_name].items():
                    if region_name == 'Global':
                        if yearly_total != 0:
                            platform_total += region_value['yearly']
#            print platform_total, yearly_total, float(platform_total) / float(yearly_total)
            if yearly_total != 0:
                line += ',' + str(float(platform_total) / float(yearly_total))
            else:
                line += ',-1'

        for region_name in region_list:
            region_total = 0
            if region_name != 'Global':
                for platform_name, platform_value in stat.items():
                    if isinstance(platform_value, dict):
                        if platform_value.has_key(region_name):
                            region_total += platform_value[region_name]['yearly']
#            print region_total, yearly_total, float(region_total) / float(yearly_total)
                if yearly_total != 0:
                    line += ',' + str(float(region_total) / float(yearly_total))
                else:
                    line += ',-1'

        for platform_name in platform_list:
            for region_name in region_list:
                if stat.has_key(platform_name) and stat[platform_name].has_key(region_name):
                    line += ',' + str(stat[platform_name][region_name]['total'])
                    line += ',' + str(stat[platform_name][region_name]['yearly'])
                else:
                    line += ',-1'
                    line += ',-1'

        line += '\n'
        outfile.write(line)

    outfile.close()

if __name__ == "__main__":
    main()


