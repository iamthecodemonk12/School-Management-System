# Generated by Django 4.1.7 on 2023-03-14 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportsubject',
            old_name='test',
            new_name='t1',
        ),
        migrations.AddField(
            model_name='reportsubject',
            name='t2',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='reportsubject',
            name='t3',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
