import os,re
from bs4 import BeautifulSoup
import httplib
import sys
import django
import unicodedata
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()
from newsdb.models import *

class NewsParser():
	fk_source_id_int=0 #Represents foreign key of Source id to store it in article_parsed table 
	
	# Function to get the local file path 
	def get_article_local_file_path(self):
		total_article_unparsed_list=[]
		article_local_directory_path_list=[]
		total_article_unparsed_list=ArticleDownload.objects.all().filter(article_download_is_parsed=0)	#Filtering only the articles whose flag is set to 0
		for each_download_article in total_article_unparsed_list:
			article_local_directory_path_list.append(each_download_article.article_download_local_file_path)
		return article_local_directory_path_list
	
	#Function for hardcoding The Hindu news source to source table
	def process_article_source(self):
		self.fk_source_id_int=0	
		article_source_check=Source.objects.filter(source_name='The Hindu')		#Checks if 'The Hindu' source is existing in the table
		if ((article_source_check.count()) > 0):								#Checks if source is existing 
			article_source_id=Source.objects.get(source_name='The Hindu')		# Getting all the details relating to source name 'The Hindu'
			self.fk_source_id_int=article_source_id.id							#Storing the source_id from the source table
		else:
			newsdb_djangoObj=Source(source_name='The Hindu')					#If it doesnt exists save to the database - Here saving the source name has 'The Hindu' in django model object
			newsdb_djangoObj.save()												#Storing the source_id from the source table
	
	#Function to parse the file content
	def process_article_content(self):
		self.process_article_source()											#Calling process_article_source() to check the source
		article_local_file_path_list=self.get_article_local_file_path()			#Calling the function and storing the list of file path in a list variable
	
		for local_file_path_str in article_local_file_path_list:				# Looping through the list of local file paths
			
			#Getting the article_download id to which the local_file_path belongs to and storing it in integer variable 
			article_download_id=ArticleDownload.objects.get(article_download_local_file_path=local_file_path_str)	
			fk_article_downlaod_id_int=article_download_id.id
			
			article_page_content=BeautifulSoup(open(local_file_path_str,'r'))	#Opening the file and converting it into a beautifulsoup object
			
			#From the beautifulsoup object finding the div tag where the content is presented
			article_div_tag_list=article_page_content.find_all("div",attrs={"id":re.compile('content\-body\-14269002\-[0-9]*')})
			if article_div_tag_list==[]:
				article_div_tag_list=article_page_content.find_all("div",attrs={"id":re.compile('content\-body\-17088308\-[0-9]*')})	
			
			if article_div_tag_list==[]:										#Suppose the content is empty write it to the log file
				the_Hindu_log_file=open("/home/mis/Documents/Newspaper/parser_log.txt","a")
				the_Hindu_log_file.write("\nArticle Skipped Parsing\t"+local_file_path_str+"\t\n")
			else:
				#If the content is present
				for div in article_div_tag_list:
					for tag in div.find_all('a'):								# Finding all the a tags and removing them
						tag.decompose()
					links_str = div.findAll('p')								#Finding all the p tags and storing in a string.
					links_str=BeautifulSoup(str(links_str)).get_text(' ',strip=True)	#Striping asll the whitespaces from it
					main_each_article_content_str=links_str
					main_each_article_content_str=unicodedata.normalize('NFKD', main_each_article_content_str).encode('ascii','ignore') #Converting the unicode characters to string
					temp_each_acrticle_content_list=main_each_article_content_str.split()
					temp_each_acrticle_content_count_int=len(temp_each_acrticle_content_list)
				
				if temp_each_acrticle_content_count_int > 25:					#Skips the article if the characters present in the article are less than 25 
					#Parsing the author name from meta tag if exists or else from the h4. If both the places it does not exist them storing it has NA
					temp_article_author_str = article_page_content.find("meta", {'name':'author'})
					if temp_article_author_str['content'] =="":
						temp_article_author_str = article_page_content.find("h4",  {'class':'home-content-name'})
						if temp_article_author_str is None:
							article_author_str='NA'
						else:
							temp_article_author_str=temp_article_author_str.text.strip()	
							article_author_list=temp_article_author_str.split('|')
							article_author_str=article_author_list[0]
					else:
						article_author_str=temp_article_author_str['content']
				
					#Parsing the article section from the webpage
					article_section_str= article_page_content.find("ul",  {'class':'breadcrumb'}) 		#Finding the section in Ul tag
					if article_section_str is None:														#If it is not available then check in meta tag
						article_section_str=article_page_content.find("meta",  property="article:section")
						article_section_str=article_section_str['content']
						article_author_str=article_author_str.replace(u'\xa0', u' ')
						if str(article_author_str[0]).lower() in str(article_section_str[0]).lower():	#If author name is section name then storing the section name has unknown
							unresolved_article_section_str="Unknown"
						else:
							#If it is not author name then search if section is below mentioned names in if . If it belongs to them then skip the article because analysis cannot be made on those section
							if article_section_str == 'Brainteasers' or article_section_str == 'Corrections & Clarifications' or article_section_str == 'Books/Reviews' or article_section_str == 'Literary Review' or article_section_str == 'Reviews' or article_section_str == 'Bombay Showcase':
								continue
							else:	
								unresolved_article_section_str=article_section_str.title()				#Store it in variable. Note: .title() is used to make the string captialized
					else:
						#If the section is found in the ul tag then do the following
						article_section_str=article_section_str.text.split() 							#Splitting to known the exact section it is mentioned in the news source
					
						#If section length is 3 
						if len(article_section_str) >= 3:												
							unresolved_article_section_str=''
							#If the sections sport/other sports 
							if article_section_str[1]=='Other':
								unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()+" "+article_section_str[2].title()
							#if the Cities or states have still sub location then storing only the main locations
							elif article_section_str[0]=='News' and article_section_str[1]=='Cities' or article_section_str[1]=='States':
								unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()
							else:
								unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()+"/"+article_section_str[2].title()
						elif len(article_section_str) == 2:
							#If length is two and the main section is Opinion then skip the whole article
							if article_section_str[0].title()=='Opinion':
								continue
							else:
								unresolved_article_section_str=''
								unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()
						else:
							if  article_section_str[0].lower() =='sport':
								unresolved_article_section_str=''
								unresolved_article_section_str=article_section_str[0].title()
							if str(article_author_str[0]).lower() in article_section_str[0].lower():
								unresolved_article_section_str="Unknown"
							else:
								unresolved_article_section_str=''
								unresolved_article_section_str=article_section_str[0].title()
				
					#Parsing the article published date from either meta tag, if it does not exist then take the date from url and assign timestamp has 00:00:00
					temp_article_published_date_str = article_page_content.find("meta",  property="article:published_time")
					article_published_date_str=temp_article_published_date_str["content"].replace('T',' ').replace('+05:30','') if temp_article_published_date_str else "NA"
					if article_published_date_str =='NA':
						article_published_date_str=local_file_path_str[30:40].replace('/','-')+' 00:00:00'
				
					#Parsing the title from h1 tag with class title 
					article_title_str = article_page_content.find("h1",  {'class':'title'})
					#If the title is not present in the above tag then we parse it from title tag and by replacing the text '- The Hindu or - Sportstarlive'
					if article_title_str is None:
						article_title_str=article_page_content.title.text
						article_title_str=article_title_str.replace(" - The Hindu",'').replace(" - Sportstarlive",'')
						#if the article title is 'The Sunday Crossword' then skip it because the article is not relevant
						if article_title_str=='The Sunday Crossword':
							continue
						else:
							article_title_str=article_title_str.encode('utf-8')						#Encoding the title with utf-8
							article_title_str=str(article_title_str);			
							article_title_str=unicode(str(article_title_str),"utf-8")				#Converting it to unicode 
							article_title_str=unicodedata.normalize('NFKD', article_title_str).encode('ascii','ignore') #Ignoring the unicode characters
					else:
						if article_title_str=='The Sunday Crossword':
							continue
						else:
							article_title_str=article_title_str.text.strip()
							article_title_str=article_title_str.encode('utf-8')
							article_title_str=str(article_title_str);			
							article_title_str=unicode(str(article_title_str),"utf-8")
							article_title_str=unicodedata.normalize('NFKD', article_title_str).encode('ascii','ignore')
				
					#Parsing the location of the article from either span tag with class blue-color ksl-time-stamp or from h4 tag with class home-content-name	
					temp_article_location_str = article_page_content.find("span",  {'class':'blue-color ksl-time-stamp'})
					if temp_article_location_str is None:
						temp_article_location_str = article_page_content.find("h4",  {'class':'home-content-name'})
						if temp_article_location_str is None:
							article_location_str=temp_article_location_str if temp_article_location_str else "Unknown"
						else:
							temp_article_location_str=temp_article_location_str.text.strip()	
							article_location_list=str(temp_article_location_str).split('|')
							try:
								temp_article_location_str=article_location_list[1]
							except IndexError:
								temp_article_location_str=article_location_list[0]	
					else:
						temp_article_location_str=temp_article_location_str.text.strip()
				
					#Replacing the characters : or , if exists in the location
					article_location_str=temp_article_location_str.title().replace(":",'')
					article_location_str=temp_article_location_str.title().replace(",",'')
				
					# Saving unresolved news type in database using django models
					fk_unresolved_news_type_id_int=0
					unresolved_news_type_id_int=0
					unresolved_newstype_check=UnresolvedNewsType.objects.filter(unresolved_news_type_name=unresolved_article_section_str)
					#If the newstype exists then skip the particular newstype else store it in the unresolve_news_type table
					if ((unresolved_newstype_check.count()) > 0):
						unresolved_news_type_id_int=UnresolvedNewsType.objects.get(unresolved_news_type_name=unresolved_article_section_str)
						fk_unresolved_news_type_id_int=unresolved_news_type_id_int.id
					else:
						unresolved_news_type_djangoobj=UnresolvedNewsType(unresolved_news_type_name=unresolved_article_section_str)
						unresolved_news_type_djangoobj.save()
						fk_unresolved_news_type_id_int=unresolved_news_type_djangoobj.id
					
					# Saving unresolved location in database using django models
					fk_unresolved_location_id_int=0
					unresolved_location_id_int=0
					unresolved_location_check=UnresolvedLocation.objects.filter(unresolved_location_name=article_location_str)
					#If the location exists then skip the particular location else store it in the unresolve_location table
					if ((unresolved_location_check.count()) > 0):
						unresolved_location_id_int=UnresolvedLocation.objects.get(unresolved_location_name=article_location_str)
						fk_unresolved_location_id_int=unresolved_location_id_int.id
					else:
						unresolved_location_djangoobj=UnresolvedLocation(unresolved_location_name=article_location_str)
						unresolved_location_djangoobj.save()
						fk_unresolved_location_id_int=unresolved_location_djangoobj.id
					
					# Saving article parsed in database using django models
					fk_article_parsed_id_int=0
					article_parsed_djangoobj=ArticleParsed(article_title=article_title_str,unresolved_news_type_id=fk_unresolved_news_type_id_int,
					published_date=article_published_date_str,unresolved_location_id=fk_unresolved_location_id_int,source_id=self.fk_source_id_int,article_download_id=fk_article_downlaod_id_int)
					article_parsed_djangoobj.save()
					fk_article_parsed_id_int=article_parsed_djangoobj.id
				
					# Saving article content in database using django models
					article_content_djangoobj=ArticleContent(article_parsed_id=fk_article_parsed_id_int,content=main_each_article_content_str[1:-1].replace('. ,','.').replace('. , ','.'))
					article_content_djangoobj.save()
					fk_article_content_id_int=article_content_djangoobj.id
				
					# Saving article author in database using django models
					article_author_djangoobj=Author(article_parsed_id=fk_article_content_id_int,author_name=article_author_str)
					article_author_djangoobj.save()
					
					ArticleDownload.objects.filter(id=fk_article_downlaod_id_int).update(article_download_is_parsed=1)
				else:
					the_Hindu_log_file=open("/home/mis/Documents/Newspaper/parser_log.txt","a")
					the_Hindu_log_file.write("\nArticle Skipped Parsing\t"+local_file_path_str+"\t\n")
					continue
				
def main():
	#Creating a object of class NewsParser()
	news_parser_obj=NewsParser()
	#Using the class object calling the process_article_content to do the parsing of the files
	news_parser_obj.process_article_content()
	return 0

if __name__ == '__main__':
	main()

