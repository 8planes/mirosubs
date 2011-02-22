# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'MessageConfig'
        db.create_table('targetter_messageconfig', (
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('os', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=200, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('browser', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('targetter', ['MessageConfig'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'MessageConfig'
        db.delete_table('targetter_messageconfig')
    
    
    models = {
        'targetter.messageconfig': {
            'Meta': {'object_name': 'MessageConfig'},
            'browser': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'os': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['targetter']
