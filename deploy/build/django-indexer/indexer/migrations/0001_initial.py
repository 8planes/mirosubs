# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Index'
        db.create_table('indexer_index', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('module_name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('column', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('indexer', ['Index'])

        # Adding unique constraint on 'Index', fields ['app_label', 'module_name', 'column', 'value', 'object_id']
        db.create_unique('indexer_index', ['app_label', 'module_name', 'column', 'value', 'object_id'])


    def backwards(self, orm):
        
        # Deleting model 'Index'
        db.delete_table('indexer_index')

        # Removing unique constraint on 'Index', fields ['app_label', 'module_name', 'column', 'value', 'object_id']
        db.delete_unique('indexer_index', ['app_label', 'module_name', 'column', 'value', 'object_id'])


    models = {
        'indexer.index': {
            'Meta': {'unique_together': "(('app_label', 'module_name', 'column', 'value', 'object_id'),)", 'object_name': 'Index'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'column': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['indexer']
