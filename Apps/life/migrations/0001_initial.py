# Generated by Django 3.1.3 on 2021-01-26 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budnum', models.CharField(max_length=50, verbose_name='楼号')),
            ],
            options={
                'verbose_name': '宿舍楼',
                'verbose_name_plural': '宿舍楼',
            },
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('floornum', models.CharField(max_length=20, verbose_name='楼层号')),
                ('budid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floor', to='life.building', verbose_name='楼号')),
            ],
            options={
                'verbose_name': '楼层',
                'verbose_name_plural': '楼层',
            },
        ),
        migrations.CreateModel(
            name='Manage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idcodetime', models.DateField(verbose_name='验证码生成时间')),
                ('idcode', models.CharField(max_length=50, verbose_name='验证码')),
                ('console', models.CharField(max_length=50, verbose_name='类型')),
            ],
            options={
                'verbose_name': '管理列表',
                'verbose_name_plural': '管理列表',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roomnum', models.CharField(max_length=20, verbose_name='房间号')),
                ('status', models.CharField(default='0', max_length=20, verbose_name='状态')),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room', to='life.floor', verbose_name='层')),
            ],
            options={
                'verbose_name': '房间',
                'verbose_name_plural': '房间',
            },
        ),
        migrations.CreateModel(
            name='TaskRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=50, verbose_name='原因')),
                ('flag', models.CharField(max_length=20, verbose_name='是否归寝')),
                ('createdtime', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('lastmodifytime', models.DateTimeField(verbose_name='最后修改时间')),
                ('buildingid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taskbuilding', to='life.building', verbose_name='楼id')),
                ('managerid', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='销假人', to='User.user', verbose_name='销假人')),
                ('objstuid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taskedstu', to='User.user', verbose_name='被执行者')),
                ('roomid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taskrecord', to='life.room', verbose_name='寝室号')),
                ('workerid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taskworker', to='User.user', verbose_name='执行者')),
            ],
            options={
                'verbose_name': '查寝记录',
                'verbose_name_plural': '查寝记录',
            },
        ),
        migrations.CreateModel(
            name='StuInRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bedposition', models.CharField(default='1', max_length=150, verbose_name='床铺位置')),
                ('status', models.CharField(default='0', max_length=50, verbose_name='是否在寝')),
                ('roomid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stuinroom', to='life.room', verbose_name='房间id')),
                ('stuid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stuinroom', to='User.user', verbose_name='学生')),
            ],
            options={
                'verbose_name': '寝室信息',
                'verbose_name_plural': '寝室信息',
            },
        ),
        migrations.CreateModel(
            name='RoomHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdtime', models.DateTimeField(auto_now=True, verbose_name='创建时间')),
                ('managerid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roomhistory', to='User.user', verbose_name='查寝人')),
                ('roomid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roomhistory', to='life.room', verbose_name='房间号')),
            ],
            options={
                'verbose_name': '寝室被查记录',
                'verbose_name_plural': '寝室被查记录',
            },
        ),
    ]
