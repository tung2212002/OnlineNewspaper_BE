# Generated by Django 4.2.4 on 2023-09-07 03:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='parent_id',
            new_name='parent',
        ),
    ]
