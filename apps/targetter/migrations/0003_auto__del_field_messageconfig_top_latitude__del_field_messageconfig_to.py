# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting field 'MessageConfig.top_latitude'
        db.delete_column('targetter_messageconfig', 'top_latitude')

        # Deleting field 'MessageConfig.top_longitude'
        db.delete_column('targetter_messageconfig', 'top_longitude')

        # Deleting field 'MessageConfig.side_length'
        db.delete_column('targetter_messageconfig', 'side_length')

        # Adding field 'MessageConfig.center_latitude'
        db.add_column('targetter_messageconfig', 'center_latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'MessageConfig.center_longitude'
        db.add_column('targetter_messageconfig', 'center_longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'MessageConfig.radius'
        db.add_column('targetter_messageconfig', 'radius', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Adding field 'MessageConfig.top_latitude'
        db.add_column('targetter_messageconfig', 'top_latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'MessageConfig.top_longitude'
        db.add_column('targetter_messageconfig', 'top_longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Adding field 'MessageConfig.side_length'
        db.add_column('targetter_messageconfig', 'side_length', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Deleting field 'MessageConfig.center_latitude'
        db.delete_column('targetter_messageconfig', 'center_latitude')

        # Deleting field 'MessageConfig.center_longitude'
        db.delete_column('targetter_messageconfig', 'center_longitude')

        # Deleting field 'MessageConfig.radius'
        db.delete_column('targetter_messageconfig', 'radius')
    
    
    models = {
        'targetter.messageconfig': {
            'Meta': {'object_name': 'MessageConfig'},
            'browser': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'center_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'center_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'os': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'radius': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['targetter']
