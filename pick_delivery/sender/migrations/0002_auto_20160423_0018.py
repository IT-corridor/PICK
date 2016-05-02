# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-23 00:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sender',
            name='gender',
            field=models.IntegerField(blank=True, choices=[(0, 'Male'), (1, 'Female')], null=True),
        ),
        migrations.AlterField(
            model_name='sender',
            name='package_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Food'), (1, 'Electironics'), (2, 'Leather'), (3, 'Machinery'), (4, 'Utility'), (5, 'Household')], null=True),
        ),
    ]