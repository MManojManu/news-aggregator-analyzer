import urllib2
import re
import os
import time
import sys
import gzip
import argparse
from django.utils import timezone
from datetime import datetime,date
import requests
import calendar
from bs4 import BeautifulSoup
from StringIO import StringIO
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()
from newsdb.models import ArticleDownload
import socket
from config import ConfigThehindu
config_thehindu_obj=ConfigThehindu()

#Path for the files to be stored locally
main_directory_path_str = "/home/mis/Documents/Newspaper/"

#Start and end date argument variables
startdate_argument_datetime=''
enddate_argument_datetime=''

#Variables declared for minimum startdate and maximum enddate
extraction_start__date_datetime=datetime.strptime('2016-01-01', '%Y-%m-%d')
extraction_end__date_datetime=datetime.strptime('2016-12-31', '%Y-%m-%d')

#Function to check if dates entered are in valid format at the time of giving command line arguments
def get_is_valid_date(validate_date_datetime):
    try:
        return datetime.strptime(validate_date_datetime, "%Y-%m-%d")
    except ValueError:
        error_message_str = "Not a valid date: '{0}'.".format(validate_date_datetime)
        raise argparse.ArgumentTypeError(error_message_str)

parser = argparse.ArgumentParser()
parser.add_argument('-s', "--startdate", help="The Start Date - format YYYY-MM-DD ",required=True,type=get_is_valid_date)
parser.add_argument('-e', "--enddate", help="The End Date format YYYY-MM-DD ", required=True,type=get_is_valid_date)
args = parser.parse_args()

#Validations for the user input dates
if args.startdate < extraction_start__date_datetime:
	print "Start Date should be after or on 2016-01-01"
	exit(1)
elif args.enddate > extraction_end__date_datetime:
	print "End Date should be before or on 2016-12-31"
	exit(1)
elif args.startdate <= args.enddate:
	startdate_argument_datetime=args.startdate
	enddate_argument_datetime=args.enddate
else:
	print 'Startdate should be lesser than enddate'
	exit(1)

#class for the news-aggregator-analyzer
class NewsAvm():
	#class variables declartion
	server_change_count_int=0 	# Used to keep a count of servers being used
	url_count_int=0 			#Count the urls to change the server
	has_folder=False 			# To check if the folder exists or not 
	log_file_fullpath_str="" 	#fullpath in a string to create a log file
	
	# Function to get webpage
	def get_webpage(self,each_day_link_str):
		server_links_list=[]
		server_links_list=config_thehindu_obj.get_server_list() #Calling the config file
		link_day_str=each_day_link_str		#Each day link
		HTTP_TIMEOUT = 5					#Timeout for connection
		
		#Creating a single day foler and also checking if it is created before
		if self.has_folder == False:
			date_unfiltered_str="".join(each_day_link_str.strip("<a href='http://www.thehindu.com/archive/web/"))
			folder_path_str=main_directory_path_str+date_unfiltered_str
			self.log_file_fullpath_str=os.path.join(folder_path_str,"log_file.txt")
			if not os.path.exists(os.path.join(folder_path_str)):
				os.makedirs(os.path.join(folder_path_str))
			self.has_folder=True
		else:
			pass
		#Dictionary of request headers for the news source The Hindu
		headers_dict = {
			'Host' : 'www.thehindu.com',
			'Connection' : 'keep-alive',
			'Upgrade-Insecure-Requests' : '1',
			'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
			'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding' : 'gzip, deflate',
			'Accept-Language' : 'en-US,en;q=0.5',
			'Proxy-Authorization' : 'Basic cHNoZW5veTowb3A4dVlKVw=='
		}
		if(self.server_change_count_int <4):		#Checking for the server count
			if(self.url_count_int < 10 ):		#Counting 10 urls to change the server
				socket.setdefaulttimeout(HTTP_TIMEOUT)	#Giving timeout for socket
				server = urllib2.ProxyHandler({'http':server_links_list[self.server_change_count_int]})	#initalize the server
				auth = urllib2.HTTPBasicAuthHandler()													
				opener = urllib2.build_opener(server,auth,urllib2.HTTPHandler)
				urllib2.install_opener(opener)
				compressed_html_page_request=urllib2.Request(link_day_str,headers=headers_dict)    		#Requesting the webpage
				attempt_retry_int=0			#Used to count the no.of attempts done
				HTTP_RETRIES=10				#No.of Retries 
				while attempt_retry_int< HTTP_RETRIES:		# 10 times the url will be retried
					attempt_retry_int+=1					#increment to 1
					try:
						compressed_html_page_content=urllib2.urlopen(compressed_html_page_request, timeout = 5).read() 	#Getting the gzip compressed website
						break
					#Prints an error in log file if there is no Internet Connection
					except urllib2.URLError, e: 
						now = timezone.now()
						log_time_datetime=now.strftime("%Y-%m-%d %H:%M:%S")
						print "No Internet Access \t Retrying URL attempt ",attempt_retry_int,"\n URL =",link_day_str
						the_Hindu_log_file=open(self.log_file_fullpath_str,"a")
						the_Hindu_log_file.write("\nNo Internet Access\t"+"Retrying URL attempt : "+str(attempt_retry_int)+"\t"+str(link_day_str)+"\t"+str(log_time_datetime)+"\t\n")
						compressed_html_page_content=""
						continue
					#Prints an error in log if there is no response from the server
					except socket.timeout:
						now = timezone.now()
						log_time_datetime=now.strftime("%Y-%m-%d %H:%M:%S")
						print "Timed out \t Retrying URL attempt ",attempt_retry_int,"\n URL =",link_day_str
						the_Hindu_log_file=open(self.log_file_fullpath_str,"a")
						the_Hindu_log_file.write("\nTimeout Error\t"+"Retrying URL attempt : "+str(attempt_retry_int)+"\t"+str(link_day_str)+"\t"+str(log_time_datetime)+"\t\n")
						compressed_html_page_content=""
						continue
				#Prints an log if the article is skipped
				if compressed_html_page_content =="":
					now = timezone.now()
					log_time_datetime=now.strftime("%Y-%m-%d %H:%M:%S")
					the_Hindu_log_file=open(self.log_file_fullpath_str,"a")
					the_Hindu_log_file.write("\nArticle Skipped\t"+str(link_day_str)+"\t"+str(log_time_datetime)+"\t\n")
					return None
				else:
					buffer_reader_html_page_content = StringIO(compressed_html_page_content)						#Storing in buffer
					decompress_html_page_content_object = gzip.GzipFile(fileobj=buffer_reader_html_page_content)	#Decompress the webpage
					decompress_html_daily_page_content= decompress_html_page_content_object.read()					#Storing the decompressed webpage
					html_daily_page_content=BeautifulSoup(decompress_html_daily_page_content)						
					self.url_count_int+=1
					now = timezone.now()
					log_time_datetime=now.strftime("%Y-%m-%d %H:%M:%S")
					the_Hindu_log_file=open(self.log_file_fullpath_str,"a")
					the_Hindu_log_file.write("\nArticle Saved\t"+str(link_day_str)+"\t"+str(log_time_datetime)+"\t\n")
					return html_daily_page_content
			else:
				self.url_count_int=0
				self.server_change_count_int+=1
		else:
			self.server_change_count_int=0
				
	# Function to get all the links of each day
	def process_each_day_url_list(self,start_date_datetime,end_date_datetime):
		#Replacing the datetime variable to int by typecasting it into string and using its functions
		startdate_replace_str=str(start_date_datetime).replace('-','/').replace('00:00:00','').replace(' ','')
		enddate_replace_str=str(end_date_datetime).replace('-','/').replace('00:00:00','').replace(' ','')
		start_year_str=startdate_replace_str[:4]
		start_month_str=startdate_replace_str[5:7]
		start_day_str=startdate_replace_str[-2:]
		end_year_str=enddate_replace_str[:4]
		end_month_str=enddate_replace_str[5:7]
		end_day_str=enddate_replace_str[-2:]
		day_url_list=[]
		days_of_month_list=[]
		days_in_month_list=[]
		day_start_date_int=int(start_day_str)
		month_start_date_int=int(start_month_str)
		for year in range(int(start_year_str),int(end_year_str)+1):				#Get the year
			for month in range(month_start_date_int,int(end_month_str)+1):		#Get the month
				days_in_month_obj = calendar.monthrange(year, month)[1]	
				days_of_month_list = [date(year, month, day) for day in range(day_start_date_int, days_in_month_obj+1)]		##Get the Day
				#Looping through the list consisting all the days
				for day in days_of_month_list:
					day_start_date_int=1		
					temp_day_str=str(day)		
					day_str=temp_day_str.split("-")
					article_date_str=day_str[0]+"/"+day_str[1]+"/"+day_str[2]
					if enddate_replace_str != article_date_str: 		
						day_url_list.append("http://www.thehindu.com/archive/web/"+day_str[0]+"/"+day_str[1]+"/"+day_str[2]+"/") #Appending the list with all the days 
					else:
						day_url_list.append("http://www.thehindu.com/archive/web/"+day_str[0]+"/"+day_str[1]+"/"+day_str[2]+"/") #Appending the list with the last day	
						break
				month_start_date_int=month_start_date_int+1
		return day_url_list
		
	#Function to get the unique ID
	def process_uniqueid(self,url_str):
		unique_article_id=str(url_str).split('/')
		if unique_article_id is None:
			pass
		else:
			each_article_unique_id_list=[]
			each_article_unique_id_list=unique_article_id[-1].replace('article','').replace('.ece','') 	#Stripping only the unique id
			if each_article_unique_id_list==[]:
				return None
			else:
				return each_article_unique_id_list
				
	#Function to process each url
	def process_each_url(self):
		day_url_list=[]
		day_url_list=self.process_each_day_url_list(startdate_argument_datetime,enddate_argument_datetime)	#Calling the function process_each_day_url_list to give all the day links
		#Looping through the day list
		for link_day in day_url_list:
				html_daily_page_content=self.get_webpage(link_day) 		#Getting the list of urls per day
				if html_daily_page_content is None:						#If it returns none then continue to the next link
					continue
				else:
					#Check for all the article links in a day which exists in <div> class: section-container and the links end with .ece 
					article_div_tag=html_daily_page_content.find_all("div",attrs={"class":"section-container"})
					article_links_perday_list=[]
					for div in article_div_tag:
						links = div.findAll('a')
						for a_tag in links:
							article_links_perday_list.append(a_tag['href']+"\n")
					article_links_perday_list=[link for link in article_links_perday_list if ".ece"  in link]
					
					#Looping through each article
					for each_article_url in article_links_perday_list:
						if "http://localhost:8080/" in each_article_url:			#There are links with localhost so skip them
							continue
						else:	
							html_each_article_content=self.get_webpage(each_article_url)
							if html_each_article_content is None:
								continue
							else:
								article_unique_id_int=self.process_uniqueid(each_article_url)		#Getting the unique ID
								print each_article_url
								article_unique_id_check=ArticleDownload.objects.filter(article_download_unique_id=article_unique_id_int) #Quering the database if article already exists
						
								if ((article_unique_id_check.count()) > 0):				#if the article exists print the message and skip the article
									print "Article "+str(article_unique_id_int)+" already exists"
									continue
								else:
									if article_unique_id_int is None:					#if there is no article id skip the article
										continue
									else:
										#Checking if the folder exists
										day_no_unfiltered_str="".join(link_day.strip("<a href='http://www.thehindu.com/archive/web/"))
										folder_path_str=main_directory_path_str+day_no_unfiltered_str
										if not os.path.exists(os.path.join(folder_path_str)):
											os.makedirs(os.path.join(folder_path_str))
										#Writing each article webpage with article uniqued ID
										each_article_filename_str=str(article_unique_id_int).strip()+'.html'
										fullpath_str=os.path.join(folder_path_str,each_article_filename_str)
										the_Hindu_archive_each_article_file=open(fullpath_str,"a")
										the_Hindu_archive_each_article_file.write(html_each_article_content.prettify().encode('utf-8'))		#Writing the file using prettify so that the webpage is stored in a html structure
										
										#Assiging the values to Django models
										now = timezone.now()
										article_created_time_datetime=now.strftime("%Y-%m-%d %H:%M:%S")
										article_last_updated_time_datetime=now.strftime("%Y-%m-%d %H:%M:%S")
										article_download_url_str=each_article_url
										article_download_unique_id_str=article_unique_id_int	
										article_download_is_parsed_flag = 0		#To set so that it tells that article is not parsed
										
										#Inserting it to the database using Django Modles with Django Object
										newsdb_djangoObj=ArticleDownload(article_download_local_file_path=fullpath_str,
											article_download_created_date=article_created_time_datetime,article_download_last_updated_date=article_last_updated_time_datetime,
											article_download_url=article_download_url_str,article_download_unique_id=article_download_unique_id_str,
											article_download_is_parsed=article_download_is_parsed_flag)
										newsdb_djangoObj.save()
										time.sleep(1)		# Delays the program by one second
def main():
		news_avm_obj=NewsAvm()
		news_avm_obj.process_each_url()
		return 0

if __name__ == '__main__':
		main()

