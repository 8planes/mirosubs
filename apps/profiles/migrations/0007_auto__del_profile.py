# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Deleting model 'Profile'
        db.delete_table('profiles_profile')
    
    
    def backwards(self, orm):
        
        # Adding model 'Profile'
        db.create_table('profiles_profile', (
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('preferred_language', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('valid_email', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('changes_notification', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('homepage', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('biography', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('profiles', ['Profile'])
    
    
    models = {
        
    }
    
    complete_apps = ['profiles']
