# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-06 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orpheus', '0006_schedule_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='description',
            field=models.CharField(default='Расписание №<django.db.models.fields.AutoField>', max_length=200, verbose_name='Описание'),
        ),
    ]