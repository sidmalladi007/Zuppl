# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zuppl', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('post_time',)},
        ),
        migrations.RemoveField(
            model_name='event',
            name='attendies',
        ),
        migrations.AlterField(
            model_name='profile',
            name='eventset',
            field=models.ManyToManyField(to='zuppl.Event', related_name='attendees'),
        ),
    ]
