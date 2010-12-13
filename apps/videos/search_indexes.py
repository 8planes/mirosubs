from haystack.indexes import *
from haystack import site
from models import Video, SubtitleLanguage

class VideoIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()
    
    def prepare(self, obj):
        self.prepared_data = super(VideoIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.__unicode__()
        return self.prepared_data
        
class SubtitleLanguageIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    title = CharField()
    language = CharField()

    def prepare(self, obj):
        self.prepared_data = super(SubtitleLanguageIndex, self).prepare(obj)
        self.prepared_data['title'] = obj.video.__unicode__()
        self.prepared_data['language'] = obj.language_display()
        return self.prepared_data
    
site.register(Video, VideoIndex)
site.register(SubtitleLanguage, SubtitleLanguageIndex)
