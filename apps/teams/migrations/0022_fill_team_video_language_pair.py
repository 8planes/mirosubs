# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.conf import settings

class Migration(DataMigration):
    
    def forwards(self, orm):
        if db.dry_run:
            return
        
        for tv in orm.TeamVideo.objects.all():
            print 'Update %s' % tv.pk
            
            langs = dict((l.language, l) for l in tv.video.subtitlelanguage_set.all())
            
            for lang0 in (item[0] for item in settings.ALL_LANGUAGES):
                
                sl0 = langs.get(lang0)
                                        
                for lang1 in (item[0] for item in settings.ALL_LANGUAGES):
                    if lang0 == lang1:
                        continue
                    
                    sl1 = langs.get(lang1)
                    sl1_subtitle_count = 0
                    
                    if sl1:
                        try:
                            last_version = sl1.subtitleversion_set.order_by('-version_no')[:1].get()
                            sl1_subtitle_count = last_version.subtitle_set.count()
                        except models.ObjectDoesNotExist:
                            pass
                    
                    if not sl1 and not sl0:
                        continue
                    
                    if not sl1 or not sl1.has_version or sl1_subtitle_count == 0:
                        if sl0 and (((sl0.is_original or sl0.is_forked) and sl0.is_complete) or (not (sl0.is_original or sl0.is_forked) and sl0.percent_done > 10)):
                            tvlp = self.get_pair_obj(orm, tv, lang0, lang1)
                            tvlp.save()    
                    elif sl1 and not (sl1.is_original or sl1.is_forked) and sl1.percent_done > 0:
                        if sl0 and sl1.standard_language == sl0 and sl0.is_complete:
                            tvlp = self.get_pair_obj(orm, tv, lang0, lang1)
                            tvlp.percent_complete = sl1.percent_done
                            tvlp.save()
                        elif sl0 and sl0.standard_language and sl0.standard_language == sl1.standard_language:
                            if sl0.standard_language.is_complete == True and sl0.percent_done > 10:
                                tvlp = self.get_pair_obj(orm, tv, lang0, lang1)
                                tvlp.percent_complete = sl1.percent_done
                                tvlp.save()  
            
    def get_pair_obj(self, orm, tv, lang0, lang1):
        tvlp = orm.TeamVideoLanguagePair()
        tvlp.team_video = tv
        tvlp.team = tv.team
        tvlp.video = tv.video
        tvlp.language_0 = lang0
        tvlp.language_1 = lang1
        tvlp.language_pair = '%s_%s' % (lang0, lang1)
        return tvlp
    
    def backwards(self, orm):
        orm.TeamVideoLanguagePair.objects.all().delete()
    
    models = {
        'auth.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'autoplay_preferences': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'award_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'changes_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'last_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'picture': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'blank': 'True'}),
            'preferred_language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'valid_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
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
        'comments.comment': {
            'Meta': {'object_name': 'Comment'},
            'content': ('django.db.models.fields.TextField', [], {'max_length': '3000'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_comment'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['comments.Comment']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'teams.application': {
            'Meta': {'unique_together': "(('team', 'user'),)", 'object_name': 'Application'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'applications'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_applications'", 'to': "orm['auth.CustomUser']"})
        },
        'teams.invite': {
            'Meta': {'unique_together': "(('team', 'user'),)", 'object_name': 'Invite'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'max_length': '200', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_invitations'", 'to': "orm['auth.CustomUser']"})
        },
        'teams.team': {
            'Meta': {'object_name': 'Team'},
            'applicants': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'applicated_teams'", 'symmetrical': 'False', 'through': "orm['teams.Application']", 'to': "orm['auth.CustomUser']"}),
            'application_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'header_html_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'highlight': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invited': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.CustomUser']", 'through': "orm['teams.Invite']", 'symmetrical': 'False'}),
            'is_moderated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'logo': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'blank': 'True'}),
            'membership_policy': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'page_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'teams'", 'symmetrical': 'False', 'through': "orm['teams.TeamMember']", 'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'intro_for_teams'", 'null': 'True', 'to': "orm['videos.Video']"}),
            'video_policy': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['videos.Video']", 'through': "orm['teams.TeamVideo']", 'symmetrical': 'False'})
        },
        'teams.teammember': {
            'Meta': {'unique_together': "(('team', 'user'),)", 'object_name': 'TeamMember'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_manager': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': "orm['teams.Team']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"})
        },
        'teams.teamvideo': {
            'Meta': {'unique_together': "(('team', 'video'),)", 'object_name': 'TeamVideo'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'all_languages': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'completed_languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['videos.SubtitleLanguage']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'thumbnail': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'teams.teamvideolanguage': {
            'Meta': {'unique_together': "(('team_video', 'language'),)", 'object_name': 'TeamVideoLanguage'},
            'forked': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'percent_done': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'team_video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': "orm['teams.TeamVideo']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'teams.teamvideolanguagepair': {
            'Meta': {'object_name': 'TeamVideoLanguagePair'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_0': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'language_1': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'language_pair': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'percent_complete': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.Team']"}),
            'team_video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['teams.TeamVideo']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['comments.Comment']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']", 'null': 'True', 'blank': 'True'}),
            'new_video_title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.subtitle': {
            'Meta': {'unique_together': "(('version', 'subtitle_id'),)", 'object_name': 'Subtitle'},
            'draft': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleDraft']", 'null': 'True'}),
            'end_time': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subtitle_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'subtitle_order': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subtitle_text': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True'})
        },
        'videos.subtitledraft': {
            'Meta': {'object_name': 'SubtitleDraft'},
            'browser_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']"}),
            'last_saved_packet': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'})
        },
        'videos.subtitlelanguage': {
            'Meta': {'unique_together': "(('video', 'language'),)", 'object_name': 'SubtitleLanguage'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followed_languages'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'has_version': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_forked': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'percent_done': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'standard_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']", 'null': 'True', 'blank': 'True'}),
            'subtitles_fetched_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'was_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
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
            'text_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'videos.usertestresult': {
            'Meta': {'object_name': 'UserTestResult'},
            'browser': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'get_updates': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task1': ('django.db.models.fields.TextField', [], {}),
            'task2': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'task3': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'videos.video': {
            'Meta': {'object_name': 'Video'},
            'allow_community_edits': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_video_urls_edit': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'followers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followed_videos'", 'blank': 'True', 'to': "orm['auth.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            's3_thumbnail': ('utils.amazon.fields.S3EnabledImageField', [], {'max_length': '100', 'blank': 'True'}),
            'subtitles_fetched_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'was_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'widget_views_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writelock_owners'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.videofeed': {
            'Meta': {'object_name': 'VideoFeed'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'})
        },
        'videos.videourl': {
            'Meta': {'object_name': 'VideoUrl'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '255'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'videoid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        }
    }
    
    complete_apps = ['videos', 'teams']
