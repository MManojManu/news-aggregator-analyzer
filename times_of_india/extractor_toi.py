# imported files

import config
import socket
from bs4 import BeautifulSoup
import requests
import urllib2
import os, sys
import datetime, calendar
import shutil
import time
import argparse
from datetime import datetime , timedelta,date
import zlib
from django.utils import timezone
import django
import cookielib
from functools import wraps

# Setup done to connect to django models and store the data in the database

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()
from newsdb.models import ArticleDownload # importing article download model to store in database


# function used to create folder with the help of url in order to store articles in proper folder

def folder_creation(url_of_each_day_str):
	path_creation_month_str = "/home/mis/Desktop/toi/2016/"+url_of_each_day_str[40:42] # to get month
	if not os.path.exists(path_creation_month_str):
		os.mkdir( path_creation_month_str, 0777)
		path_creation_day_str=path_creation_month_str+"/"+url_of_each_day_str[43:45] # to create path for each day
		if not os.path.exists(path_creation_day_str): 			# used to create folder for first time
			os.mkdir( path_creation_day_str, 0777)
	else:
		path_creation_day_str=path_creation_month_str+"/"+url_of_each_day_str[43:45] # to get day 
		if not os.path.exists(path_creation_day_str):
			os.mkdir( path_creation_day_str, 0777)	# used to create folder for rest of the time for each day
	return path_creation_day_str # returns the path to store each article

# function used to store the article in the local system and also store the data in the database

def article_save(each_article_link,each_article_path,article_download_time,proxy_server_list):
	global counter_articles_int
	global proxy_index_int
	if(counter_articles_int%10==0):
		proxy_index_int+=1
		if proxy_index_int==4:
			proxy_index_int=0
	proxy = urllib2.ProxyHandler({'http': proxy_server_list[proxy_index_int]})
	auth = urllib2.HTTPBasicAuthHandler()
	cooki=urllib2.HTTPCookieProcessor(cookies)
	opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler,cooki)
	urllib2.install_opener(opener)
	counter_articles_int+=1
	retry_page_counter_int=0
	each_article_html_page_open=""
	
	#print type(article_unique_id)
	while(retry_page_counter_int<5): #loop which retries five times in order to get the article
		try:
			#time.sleep(1)
			each_article_html_page_request=urllib2.Request(each_article_link,headers=header)
			each_article_html_page_open=urllib2.urlopen(each_article_html_page_request, timeout=20).read()
			decompressed_data=zlib.decompress(each_article_html_page_open, 16+zlib.MAX_WBITS)	
			soup_each_article_content=BeautifulSoup(decompressed_data)
			article_file_name_str=soup_each_article_content.title.text
			article_unique_id=each_article_link.split("/")
			article_unique_id=article_unique_id[-1]
			article_unique_id=article_unique_id.split(".")
			article_unique_id=article_unique_id[0]
						
			if((ArticleDownload.objects.filter(article_download_unique_id=article_unique_id).count())>0):
				#ArticleDownload.objects.filter(article_download_unique_id=article_unique_id).update(article_download_last_updated_date=article_download_time)
				print "------------------------------------------------------------------"
				print "article was already present in the database"
				print article_file_name_str
				print "-------------------------------------------------------------------"
			else:
				article_local_path_str=each_article_path+"/"+article_unique_id+".html"
				each_article_txt_file = open(article_local_path_str, "w+")
				each_article_txt_file.write(soup_each_article_content.prettify().encode('utf-8'))
				each_article_txt_file.close()
				print "--------------------------------------------------------------------------------------------------------------------------------------"
				print "Extracting article  : "+article_file_name_str
				print "Id                  : "+article_unique_id
				#print "ip address used for art     :"+urllib2.urlopen('http://www.icanhazip.com').read()
				print "--------------------------------------------------------------------------------------------------------------------------------------"
				ArticleDownload.objects.create(article_download_local_file_path=article_local_path_str,article_download_created_date=article_download_time,article_download_last_updated_date=article_download_time,article_download_url=each_article_link,article_download_unique_id=article_unique_id)
		except socket.timeout:
			print "--------------------------------------------------------------------"
			print 'caught a timeout error '
			print 'plz wait while the page will be reloaded ..........................'
			print "--------------------------------------------------------------------"
		except:
			print  "----------------------------------------------------------------------------------------------------------------------------------------"
			print each_article_link
			print "Exception has been caught"
			print "trying to get this article again................................"
			print "------------------------------------------------------------------------------------------------------------------------------------------"
		retry_page_counter_int+=1
		if(each_article_html_page_open):
			break;
# function used to generate date

def generate_date(start_date, end_date, delta_int):
    curr_date = start_date
    while curr_date < end_date:
        yield curr_date
        curr_date += delta_int


#function checks if valid dates entered

def check_valid_date(s):
	try:
		return datetime.strptime(s, "%Y-%m-%d")
	except ValueError:err_message_str = "Enter the date in '{0}' Format .".format(s)
	raise argparse.ArgumentTypeError(err_message_str)


#Start main program
date_parser = argparse.ArgumentParser(description='In order to run the Extractor for Times Of India \n You should enter the the date in the below format',epilog="Thank you")
date_parser.add_argument('-s', "--startdate", help="The Start Date format should be yyyy-mm-dd ",required=True,type=check_valid_date)
date_parser.add_argument('-e', "--enddate", help="The End Date format should be yyyy-mm-dd ", required=True,type=check_valid_date)
args = date_parser.parse_args()
header={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'en-GB,en-US;q=0.8,en;q=0.6',
	'Cache-Control':'max-age=0',
	'Connection':'keep-alive',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
	}

starttime_int=42370 # variable is used to generate the url of each day
proxy_index_int=-1  # variable is used to chane the ip
counter_articles_int=0 # count the articles and change the proxy after specified hit

# list of proxy servers
proxy_server_list=config.proxy_server_list

#conver date to datetime
start_date_time = datetime.strptime("2016-1-1", "%Y-%m-%d")
end_date_time = datetime.strptime("2016-12-31", "%Y-%m-%d")
cookies = cookielib.LWPCookieJar()

# initialization  of proxy for the first time
proxy = urllib2.ProxyHandler({'http': config.start_proxy_str})
auth = urllib2.HTTPBasicAuthHandler()
cookie_str=urllib2.HTTPCookieProcessor(cookies)
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler,cookie_str)
urllib2.install_opener(opener)


# validation for date

if(args.startdate < start_date_time ):
	print "You have Entered start date before 2016-12-31"
elif(args.enddate>end_date_time):
	print "You have Entered end date after 2016-12-31"
elif(args.startdate > args.enddate):
	print "Start date cannot be greater the end date"
else:
	start_date=(datetime.date(args.startdate))
	end_date=(datetime.date(args.enddate))
	for result_date in generate_date(date(2016, 01, 01), date(2017, 01, 01), timedelta(days=1)): #each day will be in result date
		if((result_date>=start_date) and (result_date<=end_date)): # to fetch all articles between start and end date
			each_date_str=str(result_date)  # converting date to str
			day_list=each_date_str.split("-") # splitting date by "-"
			url_of_each_day_str="http://timesofindia.indiatimes.com/"+day_list[0]+"/"+day_list[1]+"/"+day_list[2]+"/archivelist/year-"+day_list[0]+",month-"+day_list[1]+",starttime-"+str(starttime_int)+".cms" # generating url for each day
			folder_creation(url_of_each_day_str)  # sending url which has been created in order to create folder
			each_article_path=folder_creation(url_of_each_day_str) #returns the url of the folder
			each_day_html_page_request=urllib2.Request(url_of_each_day_str,headers=header) # requesting for each day page
			retry_eachday_page_counter_int=0
			each_day_html_page_open=""
			while(retry_eachday_page_counter_int<5): #loop which retries five times if there is time out
				try:
					each_day_html_page_open=urllib2.urlopen(each_day_html_page_request,timeout=20).read()     # reading each day
				except socket.timeout:
					print 'caught a timeout error '
					print 'plz wait while the page will be reloaded ..........................'
				retry_eachday_page_counter_int+=1
				if(each_day_html_page_open):
					break;
			decompressed_data=zlib.decompress(each_day_html_page_open, 16+zlib.MAX_WBITS) # decompressing using zlib
			soup_each_day=BeautifulSoup(decompressed_data)				      # converting into beautiful soup
			#import pdb;pdb.set_trace()
			print "ip address    :"+urllib2.urlopen('http://www.icanhazip.com').read() # get the proxy used first time when hitting each day page
			item=soup_each_day.find("div", {"style":"font-family:arial ;font-size:12;font-weight:bold; color: #006699"}) # find the div tag with specified attribute
			#print item.prettify()
			for each_article_link_perticularday in item.select("a[href*=timesofindia.indiatimes.com]"): # find all links in above div tag
				#print "in for loop"
				each_article_link=(each_article_link_perticularday['href']) #get only article link
				article_download_time=timezone.now()                        #Aarticle download time
				article_save(each_article_link,each_article_path,article_download_time,proxy_server_list) # function that saves article on local system and also saves in the database
		starttime_int+=1 # varible to increment starttime this variable is used to generate the url of each day
		if(result_date==end_date):
			break;
