# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'WidgetDialogLog.browser_id'
        db.add_column('uslogging_widgetdialoglog', 'browser_id', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting field 'WidgetDialogLog.browser_id'
        db.delete_column('uslogging_widgetdialoglog', 'browser_id')
    
    
    models = {
        'uslogging.widgetdialoglog': {
            'Meta': {'object_name': 'WidgetDialogLog'},
            'browser_id': ('django.db.models.fields.IntegerField', [], {}),
            'date_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'draft_pk': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {})
        }
    }
    
    complete_apps = ['uslogging']
