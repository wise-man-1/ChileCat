# Generated by Django 3.1.3 on 2020-12-13 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_auto_20201212_2106'),
    ]

    operations = [
        migrations.RenameField(
            model_name='token',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='tpost',
            name='wx_openid',
            field=models.CharField(default='', max_length=128, verbose_name='微信标识'),
        ),
    ]