# Generated by Django 5.1.2 on 2024-10-25 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0003_rename_uploadedfolder_folder'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Folder',
        ),
    ]
