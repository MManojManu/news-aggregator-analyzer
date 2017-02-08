from __future__ import print_function
from __future__ import unicode_literals
from django.contrib import admin
from .models import (ResolvedNewsType, UnresolvedNewsType, ResolvedNewsTypeUnresolvedNewsTypeMap,
                     ResolvedLocation, UnresolvedLocation, ResolvedLocationUnresolvedLocationMap,
                     Source, ArticleParsed, ArticleContent, ArticleDownload, Author,
                     )

"""This is the panel where it maps the resolved and unresolved news types"""


class ResolvedNewsTypeInline(admin.TabularInline):
    model = ResolvedNewsTypeUnresolvedNewsTypeMap
    extra = 1

"""This makes the unresolved news type available in resolved news type"""


class ResolvedNewsTypeAdmin(admin.ModelAdmin):
    inlines = [ResolvedNewsTypeInline, ]


class ResolvedNewsTypeUnresolvedNewsTypeAdmin(admin.ModelAdmin):
    fields = ['resolved_news_type', 'unresolved_news_type', ]
    list_display = ['resolved_news_type', 'unresolved_news_type', ]
    readonly_fields = ['resolved_news_type', 'unresolved_news_type', ]
    list_display_links = None


class UnresolvedNewsTypeAdmin(admin.ModelAdmin):
    fields = ['unresolved_news_type_name', ]

"""This is the panel where it maps the resolved and unresolved location"""


class ResolvedLocationInline(admin.TabularInline):
    model = ResolvedLocationUnresolvedLocationMap
    extra = 1

"""This makes the unresolved news type available in resolved location"""


class ResolvedLocationAdmin(admin.ModelAdmin):
    inlines = [ResolvedLocationInline, ]

"""This show the UnResolvedLocation"""


class UnResolvedLocationAdmin(admin.ModelAdmin):
    fields = ['unresolved_location_name', ]


class ResolvedLocationUnresolvedLocationAdmin(admin.ModelAdmin):
    fields = ['resolved_location', 'unresolved_location', ]
    list_display = ['resolved_location', 'unresolved_location', ]
    readonly_fields = ['resolved_location', 'unresolved_location', ]
    list_display_links = None


class SourceAdmin(admin.ModelAdmin):
    fields = ['source_name', ]
    list_display = ['source_name', ]


class ArticleDownloadAdmin(admin.ModelAdmin):
    fields = ['article_download_local_file_path', 'article_download_created_date',
              'article_download_last_updated_date', 'article_download_url',
              'article_download_unique_id', 'article_download_is_parsed', ]
    list_display = ['article_download_local_file_path', 'article_download_url',
                    'article_download_unique_id', 'article_download_is_parsed', ]


class ArticleParsedAdmin(admin.ModelAdmin):

    fields = ['article_title', 'unresolved_news_type',
              'published_date', 'created_date', 'last_updated_date',
              'unresolved_location', 'source', 'article_download']
    list_display = ['article_title', 'unresolved_news_type', 'published_date',
                    'created_date', 'last_updated_date', 'unresolved_location',
                    'source', 'article_download', ]
    list_filter = ['source', 'unresolved_news_type', 'unresolved_location', ]


class ArticleContentAdmin(admin.ModelAdmin):
    fields = ['article_parsed', 'content', ]
    list_display = ['article_parsed', 'content', ]


class AuthorAdmin(admin.ModelAdmin):
    fields = ['author_name', 'article_parsed', ]
    list_display = ['article_parsed', 'author_name', ]

"""admin modules are registered here"""

admin.site.register(ResolvedNewsType, ResolvedNewsTypeAdmin)
admin.site.register(UnresolvedNewsType, UnresolvedNewsTypeAdmin)
admin.site.register(ResolvedNewsTypeUnresolvedNewsTypeMap, ResolvedNewsTypeUnresolvedNewsTypeAdmin)
admin.site.register(ResolvedLocation, ResolvedLocationAdmin)
admin.site.register(UnresolvedLocation, UnResolvedLocationAdmin)
admin.site.register(ResolvedLocationUnresolvedLocationMap, ResolvedLocationUnresolvedLocationAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(ArticleDownload, ArticleDownloadAdmin)
admin.site.register(ArticleParsed, ArticleParsedAdmin)
admin.site.register(ArticleContent, ArticleContentAdmin)
admin.site.register(Author, AuthorAdmin)
