# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-05-23 00:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='context',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
