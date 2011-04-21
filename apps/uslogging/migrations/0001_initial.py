# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'WidgetDialogLog'
        db.create_table('uslogging_widgetdialoglog', (
            ('log', self.gf('django.db.models.fields.TextField')()),
            ('date_saved', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('draft_pk', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('uslogging', ['WidgetDialogLog'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'WidgetDialogLog'
        db.delete_table('uslogging_widgetdialoglog')
    
    
    models = {
        'uslogging.widgetdialoglog': {
            'Meta': {'object_name': 'WidgetDialogLog'},
            'date_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'draft_pk': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['uslogging']
