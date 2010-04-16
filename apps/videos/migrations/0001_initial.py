# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Video'
        db.create_table('videos_video', (
            ('view_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('writelock_owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='writelock_owners', null=True, to=orm['auth.User'])),
            ('video_url', self.gf('django.db.models.fields.URLField')(max_length=2048)),
            ('writelock_session_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('video_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('video_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('writelock_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('youtube_videoid', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('allow_community_edits', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('videos', ['Video'])

        # Adding model 'VideoCaptionVersion'
        db.create_table('videos_videocaptionversion', (
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('version_no', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('datetime_started', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('videos', ['VideoCaptionVersion'])

        # Adding model 'NullVideoCaptions'
        db.create_table('videos_nullvideocaptions', (
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('videos', ['NullVideoCaptions'])

        # Adding model 'NullTranslations'
        db.create_table('videos_nulltranslations', (
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('videos', ['NullTranslations'])

        # Adding model 'TranslationLanguage'
        db.create_table('videos_translationlanguage', (
            ('writelock_owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('writelock_session_key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('writelock_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('videos', ['TranslationLanguage'])

        # Adding model 'TranslationVersion'
        db.create_table('videos_translationversion', (
            ('version_no', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.TranslationLanguage'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('videos', ['TranslationVersion'])

        # Adding model 'Translation'
        db.create_table('videos_translation', (
            ('caption_id', self.gf('django.db.models.fields.IntegerField')()),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.TranslationVersion'], null=True)),
            ('null_translations', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.NullTranslations'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('translation_text', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('videos', ['Translation'])

        # Adding model 'VideoCaption'
        db.create_table('videos_videocaption', (
            ('start_time', self.gf('django.db.models.fields.FloatField')()),
            ('caption_text', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.VideoCaptionVersion'], null=True)),
            ('caption_id', self.gf('django.db.models.fields.IntegerField')()),
            ('end_time', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('null_captions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.NullVideoCaptions'], null=True)),
        ))
        db.send_create_signal('videos', ['VideoCaption'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Video'
        db.delete_table('videos_video')

        # Deleting model 'VideoCaptionVersion'
        db.delete_table('videos_videocaptionversion')

        # Deleting model 'NullVideoCaptions'
        db.delete_table('videos_nullvideocaptions')

        # Deleting model 'NullTranslations'
        db.delete_table('videos_nulltranslations')

        # Deleting model 'TranslationLanguage'
        db.delete_table('videos_translationlanguage')

        # Deleting model 'TranslationVersion'
        db.delete_table('videos_translationversion')

        # Deleting model 'Translation'
        db.delete_table('videos_translation')

        # Deleting model 'VideoCaption'
        db.delete_table('videos_videocaption')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'videos.nulltranslations': {
            'Meta': {'object_name': 'NullTranslations'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.nullvideocaptions': {
            'Meta': {'object_name': 'NullVideoCaptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.translation': {
            'Meta': {'object_name': 'Translation'},
            'caption_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_translations': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.NullTranslations']", 'null': 'True'}),
            'translation_text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.TranslationVersion']", 'null': 'True'})
        },
        'videos.translationlanguage': {
            'Meta': {'object_name': 'TranslationLanguage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.translationversion': {
            'Meta': {'object_name': 'TranslationVersion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.TranslationLanguage']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'videos.video': {
            'Meta': {'object_name': 'Video'},
            'allow_community_edits': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'video_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'video_url': ('django.db.models.fields.URLField', [], {'max_length': '2048'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writelock_owners'", 'null': 'True', 'to': "orm['auth.User']"}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'youtube_videoid': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'videos.videocaption': {
            'Meta': {'object_name': 'VideoCaption'},
            'caption_id': ('django.db.models.fields.IntegerField', [], {}),
            'caption_text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'end_time': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_captions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.NullVideoCaptions']", 'null': 'True'}),
            'start_time': ('django.db.models.fields.FloatField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.VideoCaptionVersion']", 'null': 'True'})
        },
        'videos.videocaptionversion': {
            'Meta': {'object_name': 'VideoCaptionVersion'},
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        }
    }
    
    complete_apps = ['videos']
