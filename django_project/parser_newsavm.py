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
	
	fk_source_id_int=0
	def get_article_local_file_path(self):
		total_article_count_list=[]
		article_local_directory_path_list=[]
		total_article_count_list=ArticleDownload.objects.all().filter(article_download_is_parsed=0)
		for each_download_article in total_article_count_list:
			article_local_directory_path_list.append(each_download_article.article_download_local_file_path)
		return article_local_directory_path_list
	
	#Hardcoding The Hindu news source
	def process_article_source(self):
		self.fk_source_id_int=0	
		article_source_check=Source.objects.filter(source_name='The Hindu')
		if ((article_source_check.count()) > 0):
			article_source_id=Source.objects.get(source_name='The Hindu')
			self.fk_source_id_int=article_source_id.id
		else:
			newsdb_djangoObj=Source(source_name='The Hindu')
			newsdb_djangoObj.save()
	
	def process_article_content(self):
		self.process_article_source()
		article_local_file_path=self.get_article_local_file_path()
	
		for local_file_path in article_local_file_path:
			print "local file path:",local_file_path
			article_download_id=ArticleDownload.objects.get(article_download_local_file_path=local_file_path)
			fk_article_downlaod_id_int=article_download_id.id
		
			article_page_content=BeautifulSoup(open(local_file_path,'r'))
			article_div_tag=article_page_content.find_all("div",attrs={"id":re.compile('content\-body\-14269002\-[0-9]*')})
		
			if article_div_tag==[]:
				print "Article skipped because no body content" ,local_file_path
				print "*******************************************************************************"
			else:
				for div in article_div_tag:
					links = div.findAll('p')
					links=BeautifulSoup(str(links)).get_text(' ',strip=True)
					main_each_article_content=links
					main_each_article_content=unicodedata.normalize('NFKD', main_each_article_content).encode('ascii','ignore')
					
				article_author = article_page_content.find("meta", {'name':'author'})
				if article_author['content'] =="":
					article_author_str='NA'
				else:
					article_author_str=article_author['content']
				
				article_section_str= article_page_content.find("ul",  {'class':'breadcrumb'})
				if article_section_str is None:
					article_section_str=article_page_content.find("meta",  property="article:section")
					article_section_str=article_section_str['content']
					if str(article_author_str[0]).lower() in str(article_section_str[0]).lower():
						unresolved_article_section_str="Unknown"
					else:
						if article_section_str == 'Brainteasers' or article_section_str == 'corretions & clarifications' or article_section_str == 'Books/Reviews' or article_section_str == 'Literary Review' or article_section_str == 'Reviews' or article_section_str == 'Bombay Showcase':
							continue
						else:	
							unresolved_article_section_str=article_section_str.title()
				else:
					article_section_str=article_section_str.text.split()
					if len(article_section_str) >= 3:
						unresolved_article_section_str=''
						if article_section_str[1]=='Other' and article_section_str[2]=='Sports':
							unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()+" "+article_section_str[2].title()
						elif article_section_str[0]=='News' and article_section_str[1]=='Cities' or article_section_str[1]=='States':
							unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()
						else:
							unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()+"/"+article_section_str[2].title()
					elif len(article_section_str) == 2:
						if article_section_str[0].title()=='Opinion':
							continue
						else:
							unresolved_article_section_str=''
							unresolved_article_section_str=article_section_str[0].title()+"/"+article_section_str[1].title()
					else:
						if  article_section_str[0].lower() =='sport':
							unresolved_article_section_str=''
							unresolved_article_section_str=article_section_str[0].title()
						elif str(article_author_str[0]).lower() in article_section_str[0].lower():
							unresolved_article_section_str="Unknown"
						else:
							unresolved_article_section_str=''
							unresolved_article_section_str=article_section_str[0].title()
				
				article_published_date = article_page_content.find("meta",  property="article:published_time")
				article_published_date_str=article_published_date["content"].replace('T',' ').replace('+05:30','') if article_published_date else "NA"
				if article_published_date_str =='NA':
					article_published_date_str=local_file_path[30:40].replace('/','-')+' 00:00:00'
				article_title_str = article_page_content.find("h1",  {'class':'title'})
				
				if article_title_str is None:
					article_title_str=article_page_content.title.text
					article_title_str=article_title_str.replace(" - The Hindu",'')
					if article_title_str=='The Sunday Crossword':
						continue
					else:
						article_title_str=article_title_str.encode('utf-8')
						article_title_str=str(article_title_str);			
						article_title_str=unicode(str(article_title_str),"utf-8")
						article_title_str=unicodedata.normalize('NFKD', article_title_str).encode('ascii','ignore')
				else:
					if article_title_str=='The Sunday Crossword':
						continue
					else:
						article_title_str=article_title_str.text.strip()
						article_title_str=article_title_str.encode('utf-8')
						article_title_str=str(article_title_str);			
						article_title_str=unicode(str(article_title_str),"utf-8")
						article_title_str=unicodedata.normalize('NFKD', article_title_str).encode('ascii','ignore')
				article_location = article_page_content.find("span",  {'class':'blue-color ksl-time-stamp'}).text.strip()
				article_location_str=article_location if article_location else "Unknown"
				article_location_str=article_location_str.title().replace(":",'')
				article_location_str=article_location_str.title().replace(",",'')
				
				# Saving unresolved news type in database using django models
				fk_unresolved_news_type_id_int=0
				unresolved_news_type_id_int=0
				unresolved_newstype_check=UnresolvedNewsType.objects.filter(unresolved_news_type_name=unresolved_article_section_str)
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
				if ((unresolved_location_check.count()) > 0):
					unresolved_location_id_int=UnresolvedLocation.objects.get(unresolved_location_name=article_location_str)
					fk_unresolved_location_id_int=unresolved_location_id_int.id
				else:
					unresolved_location_djangoobj=UnresolvedLocation(unresolved_location_name=article_location_str)
					unresolved_location_djangoobj.save()
					fk_unresolved_location_id_int=unresolved_location_djangoobj.id
				
				print fk_unresolved_location_id_int
				print fk_unresolved_news_type_id_int
				# Saving article parsed in database using django models
				fk_article_parsed_id_int=0
				article_parsed_djangoobj=ArticleParsed(article_title=article_title_str,unresolved_news_type_id=fk_unresolved_news_type_id_int,
				published_date=article_published_date_str,unresolved_location_id=fk_unresolved_location_id_int,source_id=self.fk_source_id_int,article_download_id=fk_article_downlaod_id_int)
				article_parsed_djangoobj.save()
				fk_article_parsed_id_int=article_parsed_djangoobj.id
				
				# Saving article content in database using django models
				article_content_djangoobj=ArticleContent(article_parsed_id=fk_article_parsed_id_int,content=main_each_article_content[1:-1])
				article_content_djangoobj.save()
				fk_article_content_id_int=article_content_djangoobj.id
				# Saving article author in database using django models
				article_author_djangoobj=Author(article_parsed_id=fk_article_content_id_int,author_name=article_author_str)
				article_author_djangoobj.save()
				
				ArticleDownload.objects.filter(id=fk_article_downlaod_id_int).update(article_download_is_parsed=1)
				
def main():
	news_parser_obj=NewsParser()
	news_parser_obj.process_article_content()
	return 0

if __name__ == '__main__':
	main()

