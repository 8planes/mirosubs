# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Rename 'name' field to 'full_name'
        db.rename_column('videos_subtitlelanguage', 'was_complete', 'had_version')




    def backwards(self, orm):
        # Rename 'full_name' field to 'name'
        db.rename_column('videos_subtitlelanguage', 'had_version', 'was_complete')

