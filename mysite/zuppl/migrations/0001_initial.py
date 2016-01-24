# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('text', models.TextField()),
                ('post_time', models.DateTimeField(auto_now_add=True, verbose_name='time published')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('created_by', models.CharField(max_length=50)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
                ('location', models.CharField(max_length=50)),
                ('campus', models.CharField(max_length=50)),
                ('start_time', models.DateTimeField(verbose_name='start time')),
                ('end_time', models.DateTimeField(verbose_name='end time')),
                ('cost', models.CharField(max_length=10, default='Free')),
                ('organizer', models.CharField(max_length=50)),
                ('organizer_email', models.EmailField(max_length=254)),
                ('details', models.TextField()),
                ('attendies', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('college', models.CharField(max_length=50)),
                ('eventset', models.ManyToManyField(to='zuppl.Event')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='event',
            field=models.ForeignKey(to='zuppl.Event'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
