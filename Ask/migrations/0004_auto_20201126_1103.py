# Generated by Django 3.1.3 on 2020-11-26 11:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
        ('Ask', '0003_ask_pass_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ask',
            name='pass_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pass_id', to='User.user', verbose_name='审批老师的id1'),
        ),
    ]