from __future__ import print_function
from __future__ import unicode_literals
from django.db import models
from datetime import datetime


class UnresolvedNewsType(models.Model):
    unresolved_news_type_name = models.CharField(max_length=250)

    def __str__(self):
        return self.unresolved_news_type_name

    class Meta:
        db_table = 'unresolved_news_type'
        verbose_name = 'UnResolved News Type'
        verbose_name_plural = "UnResolved News Types"
        managed = False


class ResolvedNewsType(models.Model):
    resolved_news_type_name = models.CharField(max_length=250)
    unresolved_news_type_map = models.ManyToManyField(UnresolvedNewsType, blank=True,
                                                      null=True, related_name='type_name',
                                                      through='ResolvedNewsTypeUnresolvedNewsTypeMap')

    def __str__(self):
        return self.resolved_news_type_name

    class Meta:
        db_table = 'resolved_news_type'
        verbose_name = 'Resolved News Type'
        verbose_name_plural = 'Resolved News Types'
        managed = False


class ResolvedNewsTypeUnresolvedNewsTypeMap(models.Model):
    resolved_news_type = models.ForeignKey(ResolvedNewsType,
                                           on_delete=models.DO_NOTHING)
    unresolved_news_type = models.ForeignKey(UnresolvedNewsType,
                                             on_delete=models.DO_NOTHING, unique=True)

    def __str__(self):
        return self.resolved_news_type.resolved_news_type_name

    class Meta:
        db_table = 'resolved_news_type_unresolved_news_type_map'
        verbose_name = 'Resolved News Type Unresolved News Type Map'
        verbose_name_plural = 'Resolved News Type Unresolved News Type Map'
        managed = False


class UnresolvedLocation(models.Model):
    unresolved_location_name = models.CharField(max_length=250)

    def __str__(self):
        return self.unresolved_location_name

    class Meta:
        db_table = 'unresolved_location'
        verbose_name = 'Unresolved Location'
        verbose_name_plural = 'Unresolved Locations'
        managed = False


class ResolvedLocation(models.Model):
    resolved_location_name = models.CharField(max_length=250, unique=True)

    unresolved_news_location_map = models.ManyToManyField(UnresolvedLocation, blank=True,
                                                          null=True, related_name='location_name',
                                                          through='ResolvedLocationUnresolvedLocationMap')

    def __str__(self):
        return self.resolved_location_name

    class Meta:
        db_table = 'resolved_location'
        verbose_name = 'Resolved Location'
        verbose_name_plural = 'Resolved Locations'
        managed = False


class ResolvedLocationUnresolvedLocationMap(models.Model):
    resolved_location = models.ForeignKey(ResolvedLocation,
                                          on_delete=models.DO_NOTHING)
    unresolved_location = models.ForeignKey(UnresolvedLocation,
                                            on_delete=models.DO_NOTHING, unique=True)

    def __str__(self):
        return self.resolved_location.resolved_location_name

    class Meta:
        db_table = 'resolved_location_unresolved_location_map'
        verbose_name = 'Resolved Location Unresolved Location Map'
        verbose_name_plural = 'Resolved Location Unresolved Location Map'
        managed = False


class Source(models.Model):
    source_name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.source_name

    class Meta:
        db_table = 'source'
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        managed = False


class ArticleDownload(models.Model):
    article_download_local_file_path = models.CharField(max_length=250)
    article_download_created_date = models.DateTimeField(default=datetime.now)
    article_download_last_updated_date = models.DateTimeField(default=datetime.now)
    article_download_url = models.CharField(max_length=250)
    article_download_unique_id = models.CharField(max_length=250)
    article_download_is_parsed = models.SmallIntegerField(max_length=1, default=0)

    def __str__(self):
        return self.article_download_unique_id

    class Meta:
        db_table = 'article_download'
        verbose_name = 'Article Download'
        verbose_name_plural = 'Article Downloads'
        managed = False


class ArticleParsed(models.Model):
    article_title = models.CharField(max_length=250)
    unresolved_news_type = models.ForeignKey(UnresolvedNewsType,
                                             on_delete=models.DO_NOTHING)
    published_date = models.DateTimeField(default=datetime.now)
    created_date = models.DateTimeField(default=datetime.now)
    last_updated_date = models.DateTimeField(default=datetime.now)
    unresolved_location = models.ForeignKey(UnresolvedLocation,
                                            on_delete=models.DO_NOTHING)
    source = models.ForeignKey(Source, on_delete=models.DO_NOTHING)
    article_download = models.ForeignKey(ArticleDownload, 
                                         on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.article_title

    class Meta:
        db_table = 'article_parsed'
        verbose_name = 'Article Parsed'
        verbose_name_plural = 'Article Parsed'
        managed = False


class ArticleContent(models.Model):
    article_parsed = models.ForeignKey(ArticleParsed, 
                                       on_delete=models.DO_NOTHING)
    content = models.TextField()

    def __str__(self):
        return self.article_parsed.article_title

    class Meta:
        db_table = 'article_content'
        verbose_name = 'Article Content'
        verbose_name_plural = 'Article Contents'
        managed = False


class Author(models.Model):
    author_name = models.CharField(max_length=250)
    article_parsed = models.ForeignKey(ArticleParsed, 
                                       on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.author_name

    class Meta:
        db_table = 'author'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        managed = False
