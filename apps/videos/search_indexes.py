from haystack.indexes import *
from haystack import site
from models import Video, TranslationLanguage

class VideoIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()
    
    def prepare(self, obj):
        self.prepared_data = super(VideoIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.__unicode__()
        self.prepared_data['language'] = 'Original'
        return self.prepared_data
        
class TranslationLanguageIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()

    def prepare(self, obj):
        self.prepared_data = super(TranslationLanguageIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.video.__unicode__()
        self.prepared_data['language'] = obj.get_language_display()
        return self.prepared_data
    
site.register(Video, VideoIndex)
site.register(TranslationLanguage, TranslationLanguageIndex)
