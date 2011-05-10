from django.db.models import signals
from django.db.models.manager import Manager
from django.core.cache import cache

from indexer.utils import Proxy

import uuid

COLUMN_SEPARATOR = '__'

class LazyIndexLookup(Proxy):
    __slots__ = ('__data__', '__instance__')

    def __init__(self, model, model_class, queryset=None, **pairs):
        object.__setattr__(self, '__data__', (model, model_class, queryset, pairs))
        object.__setattr__(self, '__instance__', None)

    def _get_current_object(self):
        """
        Return the current object.  This is useful if you want the real object
        behind the proxy at a time for performance reasons or because you want
        to pass the object into a different context.
        """
        inst = self.__instance__
        if inst is not None:
            return inst
        model, model_class, qs, pairs = self.__data__
        
        app_label = model_class._meta.app_label
        module_name = model_class._meta.module_name
        cache_key_base = ':'.join([app_label, module_name])

        if qs is None:
            qs = model_class.objects.all()

        tbl = model._meta.db_table
        main = model_class._meta.db_table
        pk = model_class._meta.pk.column
        for column, value in pairs.iteritems():
            #cid = '_i%d' % abs(hash(column))
            # print self.model.objects.filter(module_name=module_name, app_label=app_label, column=column, value=value).values_list('object_id')
            # qs = qs.filter(pk__in=self.model.objects.filter(module_name=module_name, app_label=app_label, column=column, value=value).values_list('object_id'))
            cid = tbl
            qs = qs.extra(
                # tables=['%s as %s' % (tbl, cid)],
                tables=[tbl],
                where=['%(cid)s.module_name = %%s and %(cid)s.app_label = %%s and %(cid)s.column = %%s and %(cid)s.value = %%s and %(cid)s.object_id = %(main)s.%(pk)s' % dict(
                    cid=cid,
                    pk=pk,
                    main=main,
                )],
                params=[
                    module_name,
                    app_label,
                    column,
                    value,
                ],
            )

        object.__setattr__(self, '__instance__', qs)
        return qs
    _current_object = property(_get_current_object)

class IndexManager(Manager):
    def get_for_model(self, model_class, **kwargs):
        if len(kwargs) < 1:
            raise ValueError
        
        return LazyIndexLookup(self.model, model_class, None, **kwargs)
    
    def get_for_queryset(self, queryset, **kwargs):
        if len(kwargs) < 1:
            raise ValueError
        
        return LazyIndexLookup(self.model, queryset.model, queryset, **kwargs)
    
    def register_model(self, model_class, column, index_to=None):
        """Registers a model and an index for it."""
        if model_class not in self.model.indexes:
            self.model.indexes[model_class] = set([(column, index_to)])
        else:
            self.model.indexes[model_class].add((column, index_to))
        signals.post_save.connect(self.model.handle_save, sender=model_class)
        signals.pre_delete.connect(self.model.handle_delete, sender=model_class)
    
    def remove_from_index(self, instance):
        app_label = instance._meta.app_label
        module_name = instance._meta.module_name
        tbl = self.model._meta.db_table
        self.filter(app_label=app_label, module_name=module_name, object_id=instance.pk).delete()
    
    def save_in_index(self, instance, column, index_to=None):
        """Updates an index for an instance.
        
        You may pass column as base__sub to access
        values stored deeper in the hierarchy."""
        if index_to:
            index_to = instance._meta.get_field_by_name(index_to)[0]

        if not index_to:
            app_label = instance._meta.app_label
            module_name = instance._meta.module_name
            object_id = instance.pk
        else:
            app_label = index_to.rel.to._meta.app_label
            module_name = index_to.rel.to._meta.module_name
            object_id = getattr(instance, index_to.column)

        value = instance
        first = True
        for bit in column.split(COLUMN_SEPARATOR):
            if first:
                value = getattr(value, bit)
                first = False
            elif value is not None:
                value = value.get(bit)
        if not value:
            self.filter(app_label=app_label, module_name=module_name, object_id=object_id, column=column).delete()
        else:
            # TODO: in mysql this can be a single operation
            qs = self.filter(app_label=app_label, module_name=module_name, object_id=object_id, column=column)
            if qs.exists():
                qs.update(value=value)
            else:
                self.create(app_label=app_label, module_name=module_name, object_id=object_id, column=column, value=value)

    def create_index(self, model_class, column, index_to=None):
        """Creates and prepopulates an index.
        
        You may pass column as base__sub to access
        values stored deeper in the hierarchy."""
        
        # make sure the index exists
        if index_to:
            index_to = model_class._meta.get_field_by_name(index_to)[0]

        # must pull from original data
        qs = model_class.objects.all()
        column_bits = column.split(COLUMN_SEPARATOR)

        if not index_to:
            app_label = model_class._meta.app_label
            module_name = model_class._meta.module_name
        else:
            app_label = index_to.rel.to._meta.app_label
            module_name = index_to.rel.to._meta.module_name

        for m in qs:
            if not index_to:
                object_id = m.pk
            else:
                object_id = getattr(m, index_to.column)

            value = m
            first = True
            for bit in column.split(COLUMN_SEPARATOR):
                if first:
                    value = getattr(value, bit)
                    first = False
                else:
                    value = value.get(bit)
            for bit in column_bits:
                value = value.get(bit)
            if not value:
                continue
            self.create(app_label=app_label, module_name=module_name, object_id=object_id, column=column, value=value)
        self.register_model(model_class, column)
