# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'SubtitleVersion'
        db.create_table('videos_subtitleversion', (
            ('note', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('notification_sent', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleLanguage'])),
            ('version_no', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'])),
            ('time_change', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('text_change', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime_started', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('videos', ['SubtitleVersion'])

        # Adding model 'SubtitleLanguage'
        db.create_table('videos_subtitlelanguage', (
            ('writelock_owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('writelock_session_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('is_original', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('writelock_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('was_complete', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('videos', ['SubtitleLanguage'])

        # Adding model 'Subtitle'
        db.create_table('videos_subtitle', (
            ('subtitle_id', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('start_time', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('subtitle_text', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('subtitle_order', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.SubtitleVersion'], null=True)),
            ('end_time', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('null_subtitles', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.NullSubtitles'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('videos', ['Subtitle'])

        # Adding model 'NullSubtitles'
        db.create_table('videos_nullsubtitles', (
            ('is_original', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'])),
        ))
        db.send_create_signal('videos', ['NullSubtitles'])

        # Changing field 'Action.user'
        db.alter_column('videos_action', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser'], null=True, blank=True))

        if not db.dry_run:
            self._migrate_videos(orm)

        db.create_unique('videos_subtitlelanguage', ['video_id', 'language'])

    def _migrate_videos(self, orm):
        count = orm.Video.objects.count()
        cur_video = 1
        for video in orm.Video.objects.all():
            self._migrate_video(orm, video)
            print("Migrated video {0} of {1}".format(cur_video, count))
            cur_video += 1

    def _migrate_video(self, orm, video):
        original_language = None
        if video.videocaptionversion_set.count() > 0:
            original_language = orm.SubtitleLanguage(
                video=video,
                is_original=True,
                language='',
                is_complete=video.is_subtitled,
                was_complete=video.was_subtitled)
            original_language.save()
        for vcv in video.videocaptionversion_set.all():
            self._migrate_video_caption_version(orm, vcv, original_language)
        for tl in video.translationlanguage_set.all():
            self._migrate_translation_language(orm, video, tl)
        for nvc in video.nullvideocaptions_set.all():
            self._migrate_null_video_captions(orm, nvc, video)
        for nt in video.nulltranslations_set.all():
            self._migrate_null_translations(orm, nt, video)

    def _migrate_null_video_captions(self, orm, null_video_captions, video):
        null_subtitles = orm.NullSubtitles(
            video=video,
            user=null_video_captions.user,
            is_original=True,
            language='')
        for vc in null_video_captions.videocaption_set.all():
            self._migrate_null_caption(orm, null_subtitles, vc)

    def _migrate_null_translations(self, orm, null_translations, video):
        null_subtitles = orm.NullSubtitles(
            video=video,
            user=null_translations.user,
            is_original=False,
            language=null_translations.language)
        for t in null_translations.translation_set.all():
            self._migrate_null_translation(orm, null_subtitles, t)

    def _migrate_translation_language(self, orm, video, translation_language):
        language = orm.SubtitleLanguage(
            video=video,
            is_original=False,
            language=translation_language.language,
            is_complete=translation_language.is_translated,
            was_complete=translation_language.was_translated)
        language.save()
        for tv in translation_language.translationversion_set.all():
            self._migrate_translation_version(orm, tv, language)

    def _migrate_translation_version(self, orm, translation_version, subtitle_language):
        subtitle_version = orm.SubtitleVersion(
            language=subtitle_language,
            version_no=translation_version.version_no,
            datetime_started=translation_version.datetime_started,
            user=translation_version.user,
            note=translation_version.note,
            time_change=translation_version.time_change,
            text_change=translation_version.text_change,
            notification_sent=translation_version.notification_sent,
            finished=translation_version.finished)
        subtitle_version.save()
        for t in translation_version.translation_set.all():
            self._migrate_translation(orm, t, subtitle_version)

    def _migrate_video_caption_version(self, orm, video_caption_version, original_language):
        version = orm.SubtitleVersion(
            language=original_language,
            version_no=video_caption_version.version_no,
            datetime_started=video_caption_version.datetime_started,
            user=video_caption_version.user,
            note=video_caption_version.note,
            time_change=video_caption_version.time_change,
            text_change=video_caption_version.text_change,
            notification_sent=video_caption_version.notification_sent,
            finished=video_caption_version.finished)
        version.save()
        for vc in video_caption_version.videocaption_set.all():
            self._migrate_video_caption(orm, vc, version)

    def _migrate_translation(self, orm, translation, subtitle_version):
        subtitle = orm.Subtitle(
            version=subtitle_version,
            subtitle_id=translation.caption_id,
            subtitle_text=translation.translation_text)
        subtitle.save()

    def _migrate_video_caption(self, orm, video_caption, subtitle_version):
        subtitle = orm.Subtitle(
            version=subtitle_version,
            subtitle_id=video_caption.caption_id,
            subtitle_order=video_caption.sub_order,
            subtitle_text=video_caption.caption_text,
            start_time=video_caption.start_time,
            end_time=video_caption.end_time)
        subtitle.save()

    def _migrate_null_caption(self, orm, null_subtitles, video_caption):
        subtitle = orm.Subtitle(
            null_subtitles=null_subtitles,
            subtitle_id=video_caption.caption_id,
            subtitle_order=video_caption.sub_order,
            subtitle_text=video_caption.caption_text,
            start_time=video_caption.start_time,
            end_time=video_caption.end_time)
        subtitle.save()

    def _migrate_null_translation(self, orm, null_subtitles, t):
        subtitle = orm.Subtitle(
            null_subtitles=null_subtitles,
            subtitle_id=t.caption_id,
            subtitle_text=t.translation_text)
        subtitle.save()
    
    
    def backwards(self, orm):
        
        # Deleting model 'SubtitleVersion'
        db.delete_table('videos_subtitleversion')

        # Deleting model 'SubtitleLanguage'
        db.delete_table('videos_subtitlelanguage')

        # Deleting model 'Subtitle'
        db.delete_table('videos_subtitle')

        # Deleting model 'NullSubtitles'
        db.delete_table('videos_nullsubtitles')

        # Changing field 'Action.user'
        db.alter_column('videos_action', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.CustomUser']))
    
    
    models = {
        'auth.customuser': {
            'Meta': {'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'autoplay_preferences': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'changes_notification': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'homepage': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
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
        'videos.action': {
            'Meta': {'object_name': 'Action'},
            'action_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['comments.Comment']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'new_video_title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.nullsubtitles': {
            'Meta': {'unique_together': "(('video', 'user', 'language'),)", 'object_name': 'NullSubtitles'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.nulltranslations': {
            'Meta': {'object_name': 'NullTranslations'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.nullvideocaptions': {
            'Meta': {'object_name': 'NullVideoCaptions'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.proxyvideo': {
            'Meta': {'object_name': 'ProxyVideo', '_ormbases': ['videos.Video']},
            'video_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['videos.Video']", 'unique': 'True', 'primary_key': 'True'})
        },
        'videos.stopnotification': {
            'Meta': {'object_name': 'StopNotification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        },
        'videos.subtitle': {
            'Meta': {'object_name': 'Subtitle'},
            'end_time': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_subtitles': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.NullSubtitles']", 'null': 'True'}),
            'start_time': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subtitle_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'subtitle_order': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'subtitle_text': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleVersion']", 'null': 'True'})
        },
        'videos.subtitlelanguage': {
            'Meta': {'unique_together': "(('video', 'language'),)", 'object_name': 'SubtitleLanguage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_original': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'was_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.subtitleversion': {
            'Meta': {'unique_together': "(('language', 'version_no'),)", 'object_name': 'SubtitleVersion'},
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.SubtitleLanguage']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'notification_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'text_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'videos.translation': {
            'Meta': {'object_name': 'Translation'},
            'caption_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_translations': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.NullTranslations']", 'null': 'True'}),
            'translation_text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.TranslationVersion']", 'null': 'True'})
        },
        'videos.translationlanguage': {
            'Meta': {'object_name': 'TranslationLanguage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_translated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"}),
            'was_translated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'videos.translationversion': {
            'Meta': {'object_name': 'TranslationVersion'},
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.TranslationLanguage']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'notification_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'text_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
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
            'bliptv_fileid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'bliptv_flv_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']", 'null': 'True'}),
            'subtitles_fetched_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'video_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'video_url': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'blank': 'True'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'was_subtitled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'widget_views_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'writelock_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'writelock_owners'", 'null': 'True', 'to': "orm['auth.CustomUser']"}),
            'writelock_session_key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'writelock_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'youtube_videoid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'videos.videocaption': {
            'Meta': {'object_name': 'VideoCaption'},
            'caption_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'caption_text': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'end_time': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_captions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.NullVideoCaptions']", 'null': 'True'}),
            'start_time': ('django.db.models.fields.FloatField', [], {}),
            'sub_order': ('django.db.models.fields.FloatField', [], {}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.VideoCaptionVersion']", 'null': 'True'})
        },
        'videos.videocaptionversion': {
            'Meta': {'object_name': 'VideoCaptionVersion'},
            'datetime_started': ('django.db.models.fields.DateTimeField', [], {}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'notification_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'text_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time_change': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.CustomUser']"}),
            'version_no': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']"})
        }
    }
    
    complete_apps = ['videos']
