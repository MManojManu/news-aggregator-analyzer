# import library 

import django
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
import unicodedata

#this function will store all the relevent  information to the respective tables 
def article_save(article_combine_category_str,article_published_date,article_title_str,article_url_str,article_publisher_str,article_main_content_str,location_str,article_download_id_int):
	unresolved_location_id_int=article_content_id_int=unresolved_news_type_id_int=0 #initialize
	article_published_datetime = datetime.strptime(article_published_date, "%Y/%m/%d") #converting string to datetime

	article_author_str=article_publisher_str.strip() #removing the white spaces from begg and end 
	article_title_str=article_title_str.strip()
	article_main_content_str = article_main_content_str.encode('utf-8') # encoding it to utf-8
	article_main_content_str=unicode(str(article_main_content_str),"utf-8") #converting to unciode
	article_main_content_str=unicodedata.normalize('NFKD', article_main_content_str).encode('ascii','ignore') 
	
	article_author_str = article_author_str.encode('utf-8')
	article_author_str=str(article_author_str);
	article_author_str=unicode(str(article_author_str),"utf-8")
	article_author_str=unicodedata.normalize('NFKD', article_author_str).encode('ascii','ignore')
	
	article_title_str = re.sub(r'(\s?-?\|?\s?Times of India|\s?-?\|?\s?the Times of India|\s?-?\|?\s+?Gadgets Now|\s?-?\|?\s?the Gadgets Now|\s?-?\|?\s+?Cricbuzz.com|\s?-?\|?\s?Cricbuzz.com|\s?-?\|?\s+?Times of India Photogallery|\s?-?\|?\s?the Times of India Photogallery|\s?\|\s?Hindi News|\s?\|\s?Malayalam News|\s?\|\s?Tamil News|\s?\|\s?Faridabad News|\s?\|\s?jind News|\s?\|\s?Health & Fitness News)', '', article_title_str, flags=re.IGNORECASE)
	article_title_str = article_title_str.encode('utf-8')
	article_title_str=unicode(str(article_title_str),"utf-8")
	article_title_str=unicodedata.normalize('NFKD', article_title_str).encode('ascii','ignore')
	
	print "------------------------------------------------------------------------------------------------------"
	print
	print "article category combined : ="+article_combine_category_str
	print "location "+location_str
	print article_published_datetime
	print "article title: ="+article_title_str
	print "article url ="+article_url_str
	print "article author: ="+article_publisher_str.strip()
	print article_main_content_str
	print
	print "------------------------------------------------------------------------------------------------------"


# saving the article category in the database and getting the newstype id if already exists in the database
	if(((UnresolvedNewsType.objects.filter(unresolved_news_type_name=article_combine_category_str).count())>0)):
		unresolved_news_type_id_obj=UnresolvedNewsType.objects.get(unresolved_news_type_name=article_combine_category_str)
		unresolved_news_type_id_int=unresolved_news_type_id_obj.id
	else:
		unresolved_news_type_obj=UnresolvedNewsType(unresolved_news_type_name=article_combine_category_str)
		unresolved_news_type_obj.save()
		unresolved_news_type_id_int=unresolved_news_type_obj.id
# saving the article location in the database and getting the location id if already exists in the database
	if(((UnresolvedLocation.objects.filter(unresolved_location_name=location_str).count())>0)):
		unresolved_location_id_obj=UnresolvedLocation.objects.get(unresolved_location_name=location_str)
		unresolved_location_id_int=unresolved_location_id_obj.id
	else:
		unresolved_location_obj=UnresolvedLocation(unresolved_location_name=location_str)
		unresolved_location_obj.save()
		unresolved_location_id_int=unresolved_location_obj.id
# saving the content in the article parced table and getting the id of the record
	article_parsed_obj=ArticleParsed(article_title=article_title_str,unresolved_news_type_id=unresolved_news_type_id_int,published_date=article_published_datetime,unresolved_location_id=unresolved_location_id_int,source_id=source_id_int,article_download_id=article_download_id_int)
	article_parsed_obj.save()
	article_parsed_id_int=article_parsed_obj.id
	print article_parsed_id_int
	
	article_content_obj=ArticleContent(article_parsed_id=article_parsed_id_int,content=article_main_content_str)
	article_content_obj.save()
	article_content_id_int=article_content_obj.id
	
	author_obj=Author(author_name=article_author_str,article_parsed_id=article_parsed_id_int)
	author_obj.save()
#updating the value of the is article download parsed from 0 to 1 in the article download table	
	ArticleDownload.objects.filter(id=article_download_id_int).update(article_download_is_parsed=1)


# enviornment is set up for django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()
from newsdb.models import * # all the models are being called from newsdb
all_entries_ArticleDownload = ArticleDownload.objects.all().filter(article_download_is_parsed=0) #contain all the rows in a list
#regular expressions

pattern_number_regex_str = re.compile("\d+")
pattern_numbers_five_regex_str = re.compile("\d{5}")
pattern_or_regex_str=re.compile("|")
#regex_pattern_links=re.compile("http[s]?://(?:www.youtube)|http[s]?://(?:gaana)|http[s]?://(?:youtube)|http[s]?://(?:twitter)",re.I)
#regex_pattern_link_advertisment=re.compile("watch|gaana|trailer|shoot|readalso|readmore",re.I)
count_article_skipped_int=0


# adding source name to the source table in the begg . getting the if if already present   
source_str="Times of India"

if(((Source.objects.filter(source_name=source_str).count())>0)):
	source_id_obj=Source.objects.get(source_name=source_str)
	source_id_int=source_id_obj.id
else:
	source_id_obj=Source(source_name=source_str)
	source_id_obj.save()
	source_id_int=source_id_obj.id
	
#function which takes one row each time to process

i=0
for each_row in all_entries_ArticleDownload:
	location_str="Unknown"
	article_publisher_str="NA"
	article_content=""
	article_download_id_int=each_row.id
	article_unique_id=each_row.article_download_unique_id
	article_local_path=each_row.article_download_local_file_path
	article_url_str=str(each_row.article_download_url)
	article_url_list=(article_url_str).split("/") # to find category and sub category of the news type
	article_category_str=article_url_list[4]
	article_subcategory_str=article_url_list[5]
	
	article_published_date=article_local_path[22:32]
	#print article_published_date

	if (len(article_subcategory_str)>20) or pattern_numbers_five_regex_str.search(article_subcategory_str):
		article_subcategory_str=""  # if sub category length is more then 20 

	#get the news type of an article
	if(article_subcategory_str=="" or article_category_str=="city"):
		article_combine_category_str=article_category_str.title()
	else:
		article_combine_category_str=(article_category_str+"/"+article_subcategory_str).title()
	
	if(article_category_str=="city"):#to get the location of the article
		location_str=article_subcategory_str.title()
	else:
		location_str="Unknown"
	each_article_content=open(article_local_path,"r") # each article html page is opened
	soup_each_article=BeautifulSoup(each_article_content.read()) #html page is converted to beautiful soup
	article_heading=soup_each_article.find("title")  # this is used to get title of the all f9 
	#article belongs to foll category is skipped and if there is no content for the article then the article are skipped
	if article_category_str=="articleshow" or article_combine_category_str=="Life-Style/Food":
		print "url "+article_url_str
		count_article_skipped_int+=1
		continue;
		
	try:
		article_content=soup_each_article.find("div",{"class":"section1"}) # throw exception fr some n ignore rthat
		content=(article_content.text.strip())
	except:
		try:
			article_content=soup_each_article.find("div",{"class":"Normal showpage1"}) # throw exception fr some n ignore rthat
			content=(article_content.text.strip())
		except:
			print "The article was content was not available "

	#the author cannot be taken from one tag so   

	article_title_str=(article_heading.text.strip())

	# this block tries to get the publisher of the articles from various tags 
	try:
		article_publisher_1=soup_each_article.find("span",{"class":"auth_detail"})
		article_publisher_str=(article_publisher_1.text).title()
	except:
		try:
			article_publisher_2=soup_each_article.find("a",{"class":"auth_detail"})
			article_publisher_str=(article_publisher_2.text).title()
		except:
			try:
				article_publisher=soup_each_article.find("span",{"class":"time_cptn"})
				pub_detail=(article_publisher.text)
				if (pattern_or_regex_str.search(pub_detail)):
					article_publisher_list=pub_detail.split("|")
					if (pattern_number_regex_str.search(article_publisher_list[0])):
						article_publisher_str="NA"
					else:
						article_publisher_str=(article_publisher_list[0])
			except:
				article_publisher_str="NA"

	# block throws an exception if there is any problem while pushing into table 
	try:
		if article_category_str=="entertainment": # if category is entertainment then removing all the tags mentioned below
			[div.extract() for div in article_content.find_all("div",{"class":"title"})]
			[div.extract() for div in article_content.find_all("div",{"class":"articlevideo"})]
			[span.extract() for div in article_content.find_all("div",{"class":"ytp-title-text"})]
			[twitterwidget.extract() for twitterwidget in article_content.find_all("twitterwidget",{"class":"twitter-tweet twitter-tweet-rendered"})]
			[div.extract() for div in article_content.find_all("div",{"data-type":"twitter"})]
			[div.extract() for div in article_content.find_all("div",{"class":"MediaCard-media"})]
			[div.extract() for div in article_content.find_all("div",{"class":"EmbeddedTweet-tweet"})]
			for tag in article_content.find_all('strong'):
				#if(regex_pattern_link_advertisment.search(str(tag.text))):
				tag.decompose()
		[a.extract() for a in article_content.find_all("a",attrs={"href":re.compile("http[s]?://(?:www.youtube)|http[s]?://(?:gaana)|http[s]?://(?:youtube)",re.I)})]
		print "--------------------------------------------------------------------------------------------------"
		[div.extract() for div in article_content.find_all("div",{"class":"readalso"})]# extracting the read also tag from the main content
		content=(article_content.text.strip()) # removes all blank space from start and end from the content
		content=content.replace("\n","")	# replaces /n 
		article_main_content_str=re.sub(' +',' ',content) # this is use to keep only one space in between the two words
		article_main_content_str=re.sub(r'(\s?read\s?also.?)','',article_main_content_str,flags=re.IGNORECASE) #removes the read also word
		article_save(article_combine_category_str,article_published_date,article_title_str,article_url_str,article_publisher_str,article_main_content_str,location_str,article_download_id_int)
	except:
		# the articles which are skipped the url is printed 
		#articles which does not contains body are skipped all are from article show category
		print "******************************************"
		print "url "+article_url_str
		count_article_skipped_int+=1
		print "skipped......"
		print "******************************************"

print "the number of articles ignored:= ",count_article_skipped_int
