# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'WidgetDialogCall'
        db.create_table('uslogging_widgetdialogcall', (
            ('request_args', self.gf('django.db.models.fields.TextField')()),
            ('date_saved', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('browser_id', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=127)),
        ))
        db.send_create_signal('uslogging', ['WidgetDialogCall'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'WidgetDialogCall'
        db.delete_table('uslogging_widgetdialogcall')
    
    
    models = {
        'uslogging.widgetdialogcall': {
            'Meta': {'object_name': 'WidgetDialogCall'},
            'browser_id': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'date_saved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'request_args': ('django.db.models.fields.TextField', [], {})
        },
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
