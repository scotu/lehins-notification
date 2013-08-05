# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models  


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NoticeType'
        db.create_table(u'notification_noticetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('display', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('default', self.gf('django.db.models.fields.SmallIntegerField')(default=2)),
            ('allowed', self.gf('django.db.models.fields.SmallIntegerField')(default=6)),
        ))
        db.send_create_signal(u'notification', ['NoticeType'])

        # Adding model 'NoticeSetting'
        db.create_table(u'notification_noticesetting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('notice_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['notification.NoticeType'])),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('send', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='18289300-0593-43bc-a3a5-9acccc309506', max_length=36)),
        ))
        db.send_create_signal(u'notification', ['NoticeSetting'])

        # Adding unique constraint on 'NoticeSetting', fields ['user', 'notice_type', 'medium']
        db.create_unique(u'notification_noticesetting', ['user_id', 'notice_type_id', 'medium'])

        # Adding model 'Notice'
        db.create_table(u'notification_notice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recieved_notices', to=orm['accounts.User'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_notices', null=True, to=orm['accounts.User'])),
            ('notice_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['notification.NoticeType'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('unseen', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('on_site', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
        ))
        db.send_create_signal(u'notification', ['Notice'])


    def backwards(self, orm):
        # Removing unique constraint on 'NoticeSetting', fields ['user', 'notice_type', 'medium']
        db.delete_unique(u'notification_noticesetting', ['user_id', 'notice_type_id', 'medium'])

        # Deleting model 'NoticeType'
        db.delete_table(u'notification_noticetype')

        # Deleting model 'NoticeSetting'
        db.delete_table(u'notification_noticesetting')

        # Deleting model 'Notice'
        db.delete_table(u'notification_notice')


    models = {
        u'accounts.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('crowdsite.models.fields.CrowdSmartImageField', [], {'max_length': '100', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'notification.notice': {
            'Meta': {'ordering': "['-added']", 'object_name': 'Notice'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['notification.NoticeType']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'on_site': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recieved_notices'", 'to': u"orm['accounts.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_notices'", 'null': 'True', 'to': u"orm['accounts.User']"}),
            'unseen': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'notification.noticesetting': {
            'Meta': {'unique_together': "(('user', 'notice_type', 'medium'),)", 'object_name': 'NoticeSetting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'notice_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['notification.NoticeType']"}),
            'send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'77184b8c-024e-4add-b9bd-b78eeba1a848'", 'max_length': '36'})
        },
        u'notification.noticetype': {
            'Meta': {'ordering': "['label']", 'object_name': 'NoticeType'},
            'allowed': ('django.db.models.fields.SmallIntegerField', [], {'default': '6'}),
            'default': ('django.db.models.fields.SmallIntegerField', [], {'default': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'display': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        }
    }

    complete_apps = ['notification']
