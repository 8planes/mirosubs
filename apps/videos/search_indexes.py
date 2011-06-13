from haystack.indexes import *
from haystack.models import SearchResult
from haystack import site
from models import Video, SubtitleLanguage
from comments.models import Comment
from auth.models import CustomUser as User
from utils.celery_search_index import CelerySearchIndex

SUFFIX = u' ++++++++++'

class LanguageField(SearchField):
    """
    This field is cerated for appending SUFFIX for short language code, beucase
    Solr does not want work with short strings properlly
    
    TODO: fix convering value before saving. Because SerachIndex.prepare return 
    values witch are not converted at all with field methods.
    """
    
    def prepare(self, obj):
        value = super(LanguageField, self).prepare(obj)
        return unicode(value)+SUFFIX
    
    @classmethod
    def convert(cls, value):
        if value is None:
            return None
        
        value = unicode(value)
        
        if value and value.endswith(SUFFIX):
            value = value[:-len(SUFFIX)]

        return value
    
class LanguagesField(MultiValueField):
    """
    See LanguageField
    """
    
    def prepare(self, obj):
        value = SearchField.prepare(self, obj)
        
        if value is None:
            return value
        
        value = list(value)
        
        output = []
        for val in value:
            if isinstance(val, (str, unicode)) and val:
                val = unicode(val) + SUFFIX          
            output.append(val)

        return output
        
    def convert(self, value):
        if value is None:
            return None
        
        value = list(value)

        return [v[:-len(SUFFIX)] for v in value if v.endswith(SUFFIX)]

class VideoIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField(model_attr='title_display', boost=2)
    languages = LanguagesField(faceted=True)
    video_language = LanguageField(faceted=True)
    languages_count = IntegerField(model_attr='languages_count')
    video_id = CharField(model_attr='video_id', indexed=False)
    thumbnail_url = CharField(model_attr='get_thumbnail', indexed=False)
    created = DateTimeField(model_attr='created')
    edited = DateTimeField(model_attr='edited')
    subtitles_fetched_count = IntegerField(model_attr='subtitles_fetched_count')
    widget_views_count = IntegerField(model_attr='widget_views_count')
    comments_count = IntegerField()
    
    contributors_count = IntegerField()
    activity_count = IntegerField()
    featured = DateTimeField(model_attr='featured', null=True)
    
    week_views = IntegerField()
    month_views = IntegerField()
    year_views = IntegerField()
    total_views = IntegerField(model_attr='view_count')
    
    def prepare(self, obj):
        self.prepared_data = super(VideoIndex, self).prepare(obj)
        langs = obj.subtitlelanguage_set.exclude(language=u'')
        self.prepared_data['video_language'] = obj.language
        #TODO: converting should be in Field
        self.prepared_data['video_language'] = obj.language and u'%s%s' % (obj.language, SUFFIX) or u''
        self.prepared_data['languages'] = [u'%s%s' % (lang.language, SUFFIX) for lang in langs if lang.latest_subtitles()]
        self.prepared_data['contributors_count'] = User.objects.filter(subtitleversion__language__video=obj).distinct().count()
        self.prepared_data['activity_count'] = obj.action_set.count()
        self.prepared_data['week_views'] = obj.views['week']
        self.prepared_data['month_views'] = obj.views['month']
        self.prepared_data['year_views'] = obj.views['year']
        return self.prepared_data

    def _setup_save(self, model):
        pass
    
    def _teardown_save(self, model):
        pass


class VideoSearchResult(SearchResult):
    title_for_url = Video.__dict__['title_for_url']
    get_absolute_url = Video.__dict__['_get_absolute_url']
    
    def __unicode__(self):
        title = self.title
        
        if len(title) > 70:
            title = title[:70]+'...'
        
        return title

class SubtitleLanguageIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()

    def prepare(self, obj):
        self.prepared_data = super(SubtitleLanguageIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.video.__unicode__()
        self.prepared_data['language'] = obj.language_display()
        return self.prepared_data
    
site.register(Video, VideoIndex)
#site.register(SubtitleLanguage, SubtitleLanguageIndex)
