# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2019-03-27 11:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SecondTestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_field', models.TextField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_field', models.TextField()),
                ('second_related_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_related_object', to='testapp.SecondTestModel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
