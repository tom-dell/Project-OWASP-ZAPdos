#!/usr/bin/env python

# import all the things
import time
from pprint import pprint
#from zapv2 import ZAPv2
import os
import requests
import datetime
from datetime import date

def get_details():
    # ask for the API key, depth, max children, and max times
    apikey = input("Enter your API key: ")
    try:
        depth = int(input("How far do you want the spider to crawl? Default is 5, 0 is no limit: "))
    except ValueError:
        print("Enter a number.")
    try:
        children = int(input("How many child nodes that can be crawled? Default is 10, 0 is no limit: "))
    except ValueError:
        print("Enter a number.")
    try:
        max_spider = int(input("What is the max spider time in minutes? Default is 30: "))
    except ValueError:
        print("Enter a number.")
    try:
        max_scan = int(input("What is the max scan duration in minutes? Default is 120 (2 hours): "))
    except ValueError:
        print("Enter a number.")
    print("Leave this tab open, and tail log_file.txt")

get_details()

# set API key, open list of websites and the log file
apikey = apikey
sites = open('websites.txt', 'r')
log = open('log_file.txt', 'w+')

# connect to API on port 8080 (default), and set spider max depth and max duration

#not sure if this is right?
zap = ZAPv2(apikey=apikey)
zap.spider.set_option_max_depth(depth)
zap.spider.set_option_max_children(children)

# put this in a function

for site in sites:
    # start new session, and strip the whitespace and new line chars from the line
    log.write("---------------------------------------------------------" + "\n")
    log.write("Setting new session to remove old website/s from scope." + "\n")
    zap.core.new_session()
    site = site.strip('\n')
    site = site.rstrip()
    target = site
    
    # get the current public IP & date
    # this is incase something you are scanning goes down, you can check if it was you
    ip = requests.get('http://icanhazip.com')
    ip = ip.text
    ip = ip.strip('\n')
    today = date.today()
    today = str(today)
     
    # create file names, create and open the files
    html_file_name = str(today + "-" + target + '.html')
    json_file_name = str(today + "-" + target + '.json')
    html_file_name = html_file_name.replace('/', '_')
    json_file_name = json_file_name.replace('/', '_')
    html = open(html_file_name, "w+")
    json = open(json_file_name, "w+")

    # Open the URL
    log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Accessing target %s' % (target) + "\n")
    zap.urlopen(target)
    time.sleep(2)

    # spider the URL with a timer of 30 minutes
    log.write(str(ip) + " -- " + str(datetime.datetime.now()) + " -- " + str(target) + " -- " + 'Spidering target' + "\n")
    scanid = zap.spider.scan(target)
    time.sleep(2)
                                    #set timer
    spidertimeout = time.time() + 60*30
    while (int(zap.spider.status(scanid)) < 100):
        if time.time() < spidertimeout:
            log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Spider progress %: ' + zap.spider.status(scanid) + "\n")
            time.sleep(2)
        else:
            log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Spider took to long, stopping spider and moving on to scan' + "\n")
            zap.spider.stop(scanid)
            time.sleep(5)
    log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Spider completed' + "\n")
    time.sleep(5)

    #scan the target with a timer of 2 hours
    log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Scanning target' + "\n")
    scanid = zap.ascan.scan(target, inscopeonly=False, recurse=True) 
                                    #set timer
    scantimeout = time.time() + 60*120
    while (int(zap.ascan.status(scanid)) < 100):
        if time.time() < scantimeout:
            log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Scan progress %: ' + zap.ascan.status(scanid) + "\n")
            time.sleep(5)
        else:
            log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + 'Scan took to long, stopping scan and moving onto the next website' + "\n")
            zap.ascan.stop(scanid)
            time.sleep(5)
            break

    # Report the results
    log.write(str(ip) + " -- " + str(datetime.datetime.now()) + (" -- ") + str(target) + " -- " + "Scan finished, report has been saved as HTML and JSON files in this directory" + "\n")
    html.write(zap.core.htmlreport())
    json.write(zap.core.jsonreport())
    time.sleep(2)

    # print some line breaks
    log.write("---------------------------------------------------------" + "\n")
    log.write("---------------------------------------------------------" + "\n")
    log.write("---------------------------------------------------------" + "\n")
