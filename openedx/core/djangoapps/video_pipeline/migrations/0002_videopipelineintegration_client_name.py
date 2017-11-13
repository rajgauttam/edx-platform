# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_pipeline', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='videopipelineintegration',
            name='client_name',
            field=models.CharField(default=b'VEDA-Prod', help_text='Oauth client name of video pipeline service.', max_length=100),
        ),
    ]
