# Generated by Django 3.1.2 on 2020-12-16 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Career', '0004_auto_20201215_0833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='career',
            name='source',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='地址'),
        ),
    ]
