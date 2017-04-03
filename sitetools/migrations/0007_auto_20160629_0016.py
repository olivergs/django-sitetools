# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-28 23:16
from __future__ import unicode_literals

from django.db import migrations
import sitetools.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sitetools', '0006_auto_20160627_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitelog',
            name='data',
            field=sitetools.models.fields.JSONField(blank=True, default=b'"\\"null\\""', help_text='Extra data for log message', null=True, verbose_name='Data'),
        ),
    ]
