# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'SubtitlingSession'
        db.create_table('widget_subtitlingsession', (
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subtitling_sessions', to=orm['videos.SubtitleLanguage'])),
            ('base_language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='based_subtitling_sessions', null=True, to=orm['videos.SubtitleLanguage'])),
            ('browser_id', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('parent_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleVersion'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime_started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('widget', ['SubtitlingSession'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'SubtitlingSession'
        db.delete_table('widget_subtitlingsession')
    
    
    models = {
        'auth.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'autoplay_preferences': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'award_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'changes_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'follow_new_video': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'last_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'picture': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preferred_language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'valid_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['videos.Video']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'videos.subtitlelanguage': {
            'Meta': {'unique_together': "(('video', 'language', 'standard_language'),)", 'object_name': 'SubtitleLanguage'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followed_languages'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'had_version': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'has_version': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'last_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True', 'blank': 'True'}),
            'percent_done': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'standard_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']", 'null': 'True', 'blank': 'True'}),
            'subtitle_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subtitles_fetched_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.subtitleversion': {
            'Meta': {'unique_together': "(('language', 'version_no'),)", 'object_name': 'SubtitleVersion'},
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'notification_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'result_of_rollback': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'text_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'videos.video': {
            'Meta': {'object_name': 'Video'},
            'allow_community_edits': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_video_urls_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'complete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'featured': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followed_videos'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'languages_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            's3_thumbnail': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'blank': 'True'}),
            'small_thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'subtitles_fetched_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'was_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'widget_views_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writelock_owners'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'widget.subtitlingsession': {
            'Meta': {'object_name': 'SubtitlingSession'},
            'base_language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'based_subtitling_sessions'", 'null': 'True', 'to': "orm['videos.SubtitleLanguage']"}),
            'browser_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subtitling_sessions'", 'to': "orm['videos.SubtitleLanguage']"}),
            'parent_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'})
        }
    }
    
    complete_apps = ['widget']
