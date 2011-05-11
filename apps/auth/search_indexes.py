from haystack.indexes import *
from auth.models import CustomUser as User
from haystack import site
from utils.celery_search_index import CelerySearchIndex

class UserIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    username = CharField()
    award_points = IntegerField(model_attr='award_points')
    
    def prepare_username(self, obj):
        return obj.__unicode__()
    
    def get_queryset(self):
        return super(UserIndex, self).get_queryset().filter(is_active=True)
    
site.register(User, UserIndex)
    