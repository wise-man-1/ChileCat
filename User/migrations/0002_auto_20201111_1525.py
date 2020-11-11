# Generated by Django 3.1.2 on 2020-11-11 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='identity',
            field=models.CharField(choices=[('student', '学生'), ('student', '老师'), ('ld', '领导')], default='student', max_length=20, verbose_name='身份'),
        ),
    ]
