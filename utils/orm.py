from django.db.models.sql.constants import LOOKUP_SEP
from django.db.models import sql
from django.db import connection    
from django.db.models.query import QuerySet

class LoadRelatedQuerySet(QuerySet):
    
    def __len__(self):
        val = super(LoadRelatedQuerySet, self).__len__()
        self.update_result_cache()
        return val
        
    def _fill_cache(self, num=None):
        super(LoadRelatedQuerySet, self)._fill_cache(num)
        self.update_result_cache()    

    def update_result_cache(self):
        """
        In this method check objects in self._result_cache and add realted to
        some attribute
        """
        raise Exception('Not implemented')

def load_related_generic(object_list, field='content_object'):
    if not object_list:
        return object_list

    related_field = getattr(object_list.model, field)
    ct_field = object_list.model._meta.get_field(related_field.ct_field).get_attname()
    fk_field = object_list.model._meta.get_field(related_field.fk_field).get_attname()

    result = {}
    to_retrive = {}
    for item in object_list:
        ct_id = getattr(item, ct_field)
        fk_id = getattr(item, fk_field)
        if ct_id not in to_retrive:
            to_retrive[ct_id] = {'model': getattr(item, related_field.ct_field).model_class(), 'pks': set([])}
        to_retrive[ct_id]['pks'].update([fk_id])

    for key in to_retrive:
        objects = to_retrive[key]['model']._default_manager.filter(pk__in=list(to_retrive[key]['pks']))
        result[key] = dict([[obj.pk, obj] for obj in objects])
    for item in object_list:
        setattr(item, field, result[getattr(item, ct_field)][int(getattr(item, fk_field))])

def load_related_fk(object_list, field, select_related=[]):
    if not object_list:
        return object_list

    related_field = object_list.model._meta.get_field(field)
    attname = related_field.get_attname()

    pks = list(set([getattr(obj, attname) for obj in object_list if getattr(obj, attname)]))
    objects = related_field.rel.to._default_manager.filter(pk__in=pks)
    
    if select_related:
        objects = objects.select_related(*select_related)
    
    related_dict = {}
    for obj in objects:
        related_dict[obj.pk] = obj
 
    for obj in object_list:
        try:
            setattr(obj, field, related_dict[getattr(obj, attname)])
        except KeyError:
            pass

    return object_list

def load_related_m2m(object_list, field):                                      

    select_fields = ['pk']
    related_field = object_list.model._meta.get_field(field)
    related_model = related_field.rel.to
    cache_name = 'all_%s' % field                                              

    for f in related_model._meta.local_fields:
        select_fields.append('%s%s%s' % (field, LOOKUP_SEP, f.column))         

    query = sql.Query(object_list.model)
    query.add_fields(select_fields)
    query.add_filter(('pk__in', [obj.pk for obj in object_list]))

    related_dict = {}
    cursor = connection.cursor()
    cursor.execute(str(query))

    for row in cursor.fetchall():
        if row[2]:
            related_dict.setdefault(row[0], []).append(related_model(*row[1:]))

    for obj in object_list:
        try:
            setattr(obj, cache_name, related_dict[obj.pk])
        except KeyError:
            setattr(obj, cache_name, [])

    return object_list
