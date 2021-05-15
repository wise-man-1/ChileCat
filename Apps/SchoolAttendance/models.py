from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Apps.SchoolInformation.models import *
# Create your models here.


class Rule(models.Model):
    name = models.CharField(
        max_length=30, verbose_name=u'名称', null=True, blank=True)
    message = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=u'描述')
    codename = models.CharField(max_length=8, verbose_name=u'规则代码')
    is_person = models.BooleanField(verbose_name=u'是否个人有效')

    class Meta:

        verbose_name = '规则一级分类'
        verbose_name_plural = '规则一级分类'

    def __str__(self):
        return self.name


class RuleDetails(models.Model):
    name = models.CharField(max_length=20, verbose_name=u'名称')
    score = models.IntegerField(verbose_name=u'分值', null=True, blank=True)
    rule = models.ForeignKey(
        'Rule', on_delete=models.CASCADE, verbose_name=u'一级分类')
    parent_id = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, verbose_name=u'父类')

    class Meta:

        verbose_name = '扣分详情'
        verbose_name_plural = '扣分详情'

    def __str__(self):
        return self.name


class Record(models.Model):
    """考勤记录"""
    task = models.ForeignKey(
        'Task', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="任务")
    rule_str = models.CharField(
        max_length=150, verbose_name="原因", null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, verbose_name="分值")
    rule = models.ForeignKey("RuleDetails",
                             on_delete=models.SET_NULL,
                             verbose_name="原因",
                             null=True,
                             blank=True
                             )

    room_str = models.CharField(
        max_length=20, verbose_name="寝室", null=True, blank=True)
    grade_str = models.CharField(
        max_length=20, verbose_name="班级", null=True, blank=True)

    student_approved = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="被执行者", related_name="stu_approved",
    )

    worker = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="执行者", related_name="task_worker",
    )

    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="销假人",
        related_name="销假人",
    )
    # 确保在save或者update的时候手动更新最后修改时间 因为某些批量操作不会触发
    star_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    last_time = models.DateTimeField(auto_now=True, verbose_name=u'最后修改日期')

    class Meta:
        verbose_name = '考勤记录'
        verbose_name_plural = '考勤记录'

    def __str__(self):
        """查寝记录: """
        return "考勤记录: " + str(self.id)


class Task(models.Model):
    """考勤任务管理"""
    GENDER_CHOICES1 = (
        (u'0', u'查寝'),
        (u'1', u'查卫生'),
        (u'2', u'晚自修')
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=u'创建者')
    is_open = models.BooleanField(verbose_name='是否开启')
    types = models.CharField(
        max_length=20, choices=GENDER_CHOICES1, verbose_name=u'任务类型')
    roster = models.TextField(verbose_name=u'班表', null=True, blank=True)
    college = models.ForeignKey(
        College, on_delete=models.CASCADE, verbose_name=u'分院')

    class Meta:
        """Meta definition for Manage."""

        verbose_name = '任务'
        verbose_name_plural = '任务'

    def __str__(self):
        """Unicode representation of Manage."""
        return self.user.username + "-" + self.types


class TaskPlayer(models.Model):
    '''任务-参与者
    '''
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, verbose_name=u'任务')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    is_admin = models.BooleanField(verbose_name="是否管理员")
    is_finish = models.BooleanField(verbose_name="是否完成")
    star_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建日期')
    last_time = models.DateTimeField(auto_now=True, verbose_name=u'最后修改日期')

    class Meta:
        verbose_name = '任务-参与者'


class TaskFloor(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, verbose_name=u'考勤任务')
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, verbose_name=u'楼')

    class Meta:
        verbose_name = '任务关联楼'


class TaskClass(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, verbose_name=u'考勤任务')
    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE, verbose_name=u'班级')

    class Meta:
        verbose_name = '任务关班级'


class RoomHistory(models.Model):
    """考勤-房间
    记录房间是否被检查的状态，记录这个房间是否被点名和查卫生执行过
    """
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, verbose_name="房间号", related_name="room_history"
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, verbose_name=u'任务')
    is_knowing = models.BooleanField(verbose_name='是否点名')
    is_health = models.BooleanField(verbose_name='是否查卫生')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '寝室被查记录'
        verbose_name_plural = '寝室被查记录'

    def __str__(self):
        return self.room.floor.building.name + self.room.floor.name + self.room.name


class TaskFloorStudent(models.Model):
    '''考勤-房间-学生
    记录房间里面的学生检查状态 是   缺寝 还是 在寝
    '''
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, verbose_name=u'任务')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=u'用户')
    flg = models.BooleanField(verbose_name='是否在寝室')

    def __str__(self):
        return self.user.username + is_in

    class Meta:
        verbose_name_plural = '学生在寝情况'


class UserCall(models.Model):
    '''点名-学生
    当学生在点名的时候被记录就变动点名类型
    '''
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, verbose_name=u'任务')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=u'用户')
    rule = models.ForeignKey("RuleDetails", on_delete=models.CASCADE,
                             verbose_name="第几次点名", null=True, blank=True)