'''
Author: 邹洋
Date: 2021-05-20 08:37:12
Email: 2810201146@qq.com
LastEditors:  
LastEditTime: 2021-12-05 15:27:43
Description: 
'''
import datetime

from django.http import request

from Apps.SchoolAttendance.pagination import RecordQueryrPagination
from Apps.User.utils.auth import get_token_by_user
from cool.views import CoolAPIException, CoolBFFAPIView, ErrorCode, ViewSite
from core.common import get_end_date, get_start_date
from core.excel_utils import ExcelBase
from core.query_methods import Concat
from core.settings import *
from core.views import *
from django.contrib.auth import get_user_model
from django.db.models import F, manager, query
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import fields

from . import models, serializers

User = get_user_model()

site = ViewSite(name='SchoolInformation', app_name='SchoolInformation')


@site
class TaskObtain(PermissionView):

    name = _('获取任务')
    response_info_serializer_class = serializers.TaskObtain

    def get_context(self, request, *args, **kwargs):
        task = models.Task.objects.filter(
            admin=request.user, types=request.params.type
        ).select_related('college')
        return serializers.TaskObtain(task, many=True, request=request).data

    class Meta:
        param_fields = (
            (
                'type',
                fields.CharField(
                    label=_('任务类型'), max_length=1, help_text=' 0晚查寝 1查卫生 2晚自修'
                ),
            ),
        )


@site
class TaskSwitch(TaskBase):

    name = _('开启/关闭任务')
    response_info_serializer_class = serializers.TaskSwitch

    def get_context(self, request, *args, **kwargs):
        task = self.get_task_by_user()
        task.is_open = not task.is_open
        task.save()
        return serializers.TaskSwitch(task, request=request).data


@site
class TaskRestKnowing(TaskBase):
    name = _('重置查寝任务状态')

    def get_context(self, request, *args, **kwargs):
        task = self.get_task_by_user()
        models.RoomHistory.objects.filter(task=task).update(
            is_knowing=False
        )  # 所有寝室为未检查
        models.TaskFloorStudent.objects.filter(task=task).update(flg=True)  # 所有学生为在寝


@site
class TaskRestLate(TaskBase):
    name = _('重置晚自修任务状态')

    def get_context(self, request, *args, **kwargs):
        task = self.get_task_by_user()
        models.UserCall.objects.filter(task=task).update(flg=None)


@site
class TaskRestHealth(TaskBase):
    name = _('重置卫生检查任务状态')

    def get_context(self, request, *args, **kwargs):
        task = self.get_task_by_user()
        models.RoomHistory.objects.filter(task=task).update(is_health=False)


@site
class Scheduling(TaskBase):
    name = _('获取排版表')

    def get_context(self, request, *args, **kwargs):
        return json.loads(self.get_task_by_user().roster)


@site
class SchedulingUpdateKnowing(TaskBase):
    name = _('修改查寝班表')

    def get_context(self, request, *args, **kwargs):
        roster = request.params.roster
        user_list = []
        error = 0
        for item in roster:
            for layer in item['layer_list']:
                for user in layer['user']:
                    if len(item['title'][:1]) != 0 and len(user['username']) != 0:
                        try:
                            u = User.objects.get(username=user['username'])
                            user_list.append(u)
                        except:
                            error += 1

        self.init_scheduling(user_list, roster)
        if error != 0:
            return str(error) + '个学生排班失败'

    class Meta:
        param_fields = (('roster', fields.JSONField(label=_('班表'))),)


@site
class SchedulingUpdateLate(TaskBase):
    name = _('修改晚自修班表')

    def get_context(self, request, *args, **kwargs):
        roster = request.params.roster
        user_list = []
        roster_new = []
        for item in roster:
            u = User.objects.filter(username=item['username'])
            if len(u) == 1:
                user_list.append(u[0])
                roster_new.append(item)

        self.init_scheduling(user_list, roster_new)
        return '执行成功' + '更新' + str(len(roster_new)) + '个学生'

    class Meta:
        param_fields = (('roster', fields.JSONField(label=_('班表'))),)


@site
class Condition(TaskBase):

    name = _('考勤学生记录情况')
    response_info_serializer_class = serializers.ConditionRecord

    def get_context(self, request, *args, **kwargs):
        # 开始时间和结束时间
        start_date = get_start_date(request)
        end_date = get_end_date(request)

        # 楼-层筛选
        building = request.params.building
        floor = request.params.floor
        q_floor = Q()
        if building and floor:
            query_str = building + '#' + floor
            q_floor = Q(room_str__startswith=query_str)


        records = (
            models.Record.objects.filter(
                q_floor,
                task=self.get_task_by_user(),
                manager=None,
                star_time__range=(start_date, end_date),
            )
            .select_related('rule')
            .order_by('-last_time')
        )

        return serializers.ConditionRecord(records, request=request, many=True).data
    class Meta:

        param_fields = (
            ('building', fields.CharField(label=_('楼'),default=None)),
            ('floor', fields.CharField(label=_('层'),default=None)),
            ('start_date', fields.DateField(label=_('开始日期'), default=None)),
            ('end_date', fields.DateField(label=_('结束日期'), default=None)),
        )


@site
class UndoRecord(TaskBase,RecordBase):
    name = _('销假(当前任务管理员)')

    def get_context(self, request, *args, **kwargs):
        task = self.get_task_by_user()
        id = request.params.record_id
        record = self.get_record_by_id_task(id,task)
        self.undo_record(record,request.user)


    class Meta:
        param_fields = (
            ('record_id', fields.CharField(label=_('考勤记录ID'), max_length=8)),
        )


@site
class UndoRecordAdmin(PermissionView,RecordBase):
    name = _('销假(分院管理员)')
    need_permissions = ('SchoolAttendance.undo_record_admin',)

    def get_context(self, request, *args, **kwargs):
        # TODO 需要进行管理员身份验证,并且只能对自己分院有效
        id = request.params.record_id
        record = self.get_record_by_id(id)
        self.undo_record(record,request.user)

    class Meta:
        param_fields = (
            ('record_id', fields.CharField(label=_('考勤记录ID'), max_length=8)),
        )


@site
class TaskExecutor(PermissionView):
    name = _('工作者获取任务')
    response_info_serializer_class = serializers.TaskExecutor

    def get_context(self, request, *args, **kwargs):
        tasks = models.TaskPlayer.objects.filter(user=request.user, task__is_open=True)
        return serializers.TaskExecutor(tasks, many=True, request=request).data


@site
class knowingExcelOut(TaskBase,ExcelBase):
    name = _('当天考勤数据导出')
    response_info_serializer_class = serializers.TaskRecordExcelSerializer

    def check_api_permissions(self, request, *args, **kwargs):
        pass

    def get_context(self, request, *args, **kwargs):
        get_token_by_user(request)
        task = self.get_task_by_user()
        now = datetime.date.today()
        records = models.Record.objects.filter(
            task=task,
            manager=None,
            star_time__date=datetime.date(now.year, now.month, now.day),
        ).order_by('-last_time')
        if not records:
            raise CoolAPIException(ErrorCode.EXCEL_OUT_NO_DATA)
        ser_records = serializers.TaskRecordExcelSerializer(
            instance=records, many=True
        ).data
        header = ['日期','楼号','班级','学号','姓名','原因']
        return self.download_excel(ser_records,'学生考勤表',header,2)

    class Meta:
        param_fields = (('token', fields.CharField(label=_('token'))),)


@site
class Rule(CoolBFFAPIView):
    name = _('获取规则')

    def get_context(self, request, *args, **kwargs):
        codename = request.params.codename
        rule = models.Rule.objects.get(codename=codename)
        data = rule.ruledetails_set.exclude(name__endswith=CUSTOM_RULE).values(
            'id', 'name', 'parent_id', 'score'
        )
        return list(data)

    class Meta:
        param_fields = (('codename', fields.CharField(label=_('规则编号'))),)


@site
class SubmitLateDiscipline(SubmitBase):
    name = _('晚自修考勤 违纪提交')

    def get_custom_rule(self):
        '''获取自定义规则'''
        return create_custom_rule(RULE_CODE_03, RULE_NAME_03_01)

    def submit_check(self, record_model, record):
        '''提交学生考勤记录'''
        if record['reason_is_custom']:
            if len(record_model['rule_str']) <= 0:
                raise CoolAPIException(ErrorCode.THE_REASON_IS_EMPTY)

            score = int(record_model['score'])
            if score <= 0 or score > 10:
                raise CoolAPIException(ErrorCode.CUSTOM_SCORE_ERROR)

            record_model['score'] = record['score']


@site
class SubmitLate(SubmitBase):
    name = _('晚自修考勤 点名提交')

    def submit_check(self, record_model, record):
        '''提交学生考勤记录'''
        call, status = models.UserCall.objects.get_or_create(
            task=self.task,
            user=record_model['student_approved'],
            rule=record_model['rule'],
        )
        # 判断是不是本次任务第一次点名
        is_none = call.flg == None
        if is_none:
            call.flg = self.request.params.flg
            call.save()
            return not self.request.params.flg
        return is_none

    class Meta:
        param_fields = (('flg', fields.BooleanField(label=_('点名 在/不在'))),)


@site
class SubmitKnowing(SubmitBase):
    name = _('寝室考勤 点名提交')

    def get_custom_rule(self):
        '''获取自定义规则'''
        return create_custom_rule(RULE_CODE_01, RULE_NAME_01_01)

    def updata_user_in_room(self, user, is_flg):
        '''学生在宿舍情况'''
        if is_flg == False:
            user_in_room, flg = models.TaskFloorStudent.objects.get_or_create(
                task=self.task, user=user
            )
            # TODO 多线程需要保证原子性
            if user_in_room.flg == False:  # 如果状态为不在寝室 就不进行提交
                return False
            else:
                user_in_room.flg = is_flg
                user_in_room.save()
        elif is_flg == True:
            models.TaskFloorStudent.objects.filter(task=self.task, user=user).update(
                flg=True
            )

    def submit_undo_record(self,record_model,user):
        self.updata_user_in_room(record_model['student_approved'], True)
        record_model['rule_str'] = '查寝：误操作撤销'

        # 定位记录 时间 任务 被撤销学生
        now = datetime.datetime.now()
        records = models.Record.objects.filter(
            task=self.task,
            student_approved=record_model['student_approved'],
            star_time__date=datetime.date(now.year, now.month, now.day),
        )

        manager_user = record_model['manager']
        if len(records) == 1:
            record = records[0]
            self.undo_record(record,manager_user)
        elif len(records) > 1:
            records.update(manager=manager_user)


    def submit_check(self, record_model, record):
        '''提交学生考勤记录'''
        return self.updata_user_in_room(record_model['student_approved'], False)

    class Meta:
        param_fields = (('room_id', fields.CharField(label=_('房间ID'))),)


@site
class SubmitHealth(SubmitBase):
    name = _('寝室卫生 检查提交')

    def get_custom_rule(self):
        '''获取自定义宿舍卫生规则'''
        return create_custom_rule(RULE_CODE_07, RULE_NAME_07_01)

    def submit_check(self, record_model, record):
        '''提交学生考勤记录'''
        pass

    class Meta:
        param_fields = (('room_id', fields.CharField(label=_('房间ID'))),)


@site
class DormStoreyInfo(TaskBase):
    name = _('楼内层列表')

    def get_context(self, request, *args, **kwargs):
        self.get_task()  # TODO 可以优化查询
        buildings = self.task.buildings.all()
        buildings_info = []
        for building in buildings:
            info = {"list": [], 'id': building.id, 'name': building.name + "号楼"}
            floors = building.floor.filter(is_open=True).order_by('name')
            for floor in floors:
                floor = {'id': floor.id, 'name': "第" + floor.name + "层"}
                info['list'].append(floor)
            buildings_info.append(info)
        return buildings_info


@site
class DormRoomInfo(TaskBase):
    name = _('层内房间列表')

    response_info_serializer_class = serializers.DormRoomInfo

    def get_context(self, request, *args, **kwargs):
        self.get_task()  # TODO 可以优化查询
        floor_id = request.params.floor_id
        rooms = models.Room.objects.filter(floor_id=floor_id,stu_in_room__is_active=True).distinct().order_by('name')
        return serializers.DormRoomInfo(rooms, many=True, request=request).data

    class Meta:
        param_fields = (('floor_id', fields.CharField(label=_('楼层ID'))),)


@site
class DormStudentRoomInfo(TaskBase):
    name = _('房间学生 信息')
    response_info_serializer_class = serializers.DormStudentRoomInfo

    def get_context(self, request, *args, **kwargs):
        self.get_task()
        room_id = request.params.room_id
        rooms = models.StuInRoom.objects.filter(room_id=room_id).select_related('user')
        return serializers.DormStudentRoomInfo(rooms, many=True, request=request).data

    class Meta:
        param_fields = (('room_id', fields.CharField(label=_('房间ID'))),)


@site
class StudentDisciplinary(CoolBFFAPIView):
    name = _('学生查看公告')
    response_info_serializer_class = serializers.StudentDisciplinary

    def get_context(self, request, *args, **kwargs):
        # TODO 优化为仅支持查看本学院的情况
        task_id_list = models.Task.objects.filter(types='0').values_list(
            'id', flat=True
        )
        now = datetime.datetime.now()
        records = models.Record.objects.filter(
            task__in=task_id_list,
            manager=None,
            star_time__date=datetime.date(now.year, now.month, now.day),
        ).order_by('-last_time')
        return serializers.StudentDisciplinary(records, many=True).data


@site
class LateClass(TaskBase):
    name = _('晚自修点名 名单数据')

    def get_context(self, request, *args, **kwargs):
        self.get_task_player_by_user()
        type_ = int(request.params.type)
        if type_ == 0:
            grades = self.task.grades.all().values('id', 'name')
            return list(grades)
        elif type_ == 1:
            class_id = request.params.class_id
            rule_id = request.params.rule_id
            users = User.objects.filter(grade__id=class_id)
            calls = models.UserCall.objects.filter(
                user__in=users, task=self.request.task, rule_id=rule_id
            ).select_related('user')
            if users.count() != calls.count():
                call_list = list()
                for u in users:
                    #     call_list.append(UserCall(task=self.request.task,user=u,rule_id=rule_id))
                    # UserCall.objects.bulk_create(call_list)
                    # TODO 这里的加载应该在系统初始化的时候就完成 并且提供手动更新的接口 当然更应该使用缓存
                    UserCall.objects.get_or_create(
                        task=self.request.task, user=u, rule_id=rule_id
                    )
                calls = models.UserCall.objects.filter(
                    user__in=users, task=self.request.task, rule_id=rule_id
                ).select_related('user')
            return serializers.UserCallSerializer(
                calls, request=request, many=True
            ).data

    class Meta:
        param_fields = (
            ('rule_id', fields.CharField(label=_('规则ID'), default=None)),
            ('class_id', fields.CharField(label=_('班级ID'), default=None)),
            (
                'type',
                fields.CharField(
                    label=_('类型'), help_text="0 # 获取任务绑定的班级 1 # 获取班级名单附带学生多次点名情况"
                ),
            ),
        )


@site
class RecordQuery(CoolBFFAPIView):
    name = _('考勤查询')

    def get_context(self, request, *args, **kwargs):
        username = request.params.username
        college_id = request.params.college_id
        start_date = request.params.start_date
        end_date = request.params.end_date
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        end_date = datetime.datetime(
            end_date.year, end_date.month, end_date.day, 23, 59, 59
        )
        q4 = Q(task__types__in=['2', '0','3']) | Q(rule_str='早签')  # 任务类型限制
        q5 = Q(task__college__id=college_id)  # 分院
        q6 = Q(rule__isnull=False)

        records = (
            models.Record.objects.filter(
                q4, q5,q6,  star_time__range=(start_date, end_date), manager__isnull=True
            )
            .select_related('student_approved', 'worker', 'rule', 'task__college')
            .order_by('-last_time')
        )

        if username:
            try:
                user = User.objects.filter(Q(username=username) | Q(name=username))
                records = records.filter(student_approved__in=user)
            except:
                records = []
                raise CoolAPIException(ErrorCode.ABNORMAL_ATTENDANCE)
                
        pg = RecordQueryrPagination()
        page_roles = pg.paginate_queryset(queryset=records, request=request, view=self)
        ser = serializers.RecordQuery(instance=page_roles, many=True).data
        return {"total": len(records), "results": ser, "page_size": pg.page_size}

    class Meta:
        param_fields = (
            ('username', fields.CharField(label=_('用户名'), default=None)),
            ('college_id', fields.IntegerField(label=_('分院ID'))),
            ('start_date', fields.CharField(label=_('开始时间'))),
            ('end_date', fields.CharField(label=_('结束时间'))),
        )


@site
class PersonalDisciplineQuery(PermissionView):
    name = _('个人违纪查询')
    response_info_serializer_class = serializers.PersonalDisciplineQuery

    def get_context(self, request, *args, **kwargs):
        # 用户过滤条件
        q_user = Q(student_approved=request.user,manager__isnull=True)
        
        # 查询我的寝室
        room = request.params.room
        q_room = Q()
        if room:
            q_user = Q()
            try:
                room = StuInRoom.objects.get(user=request.user).room.__str__()
            except:
                raise CoolAPIException(ErrorCode.DORMITORY_NOT_ARRANGED)
            q_room = Q(room_str = room)

        data =Record.objects.filter(q_user,q_room,).select_related('worker').order_by('-last_time')
        return serializers.PersonalDisciplineQuery(instance=data, many=True, request=request).data
    class Meta:
        param_fields = (
            ('room', fields.BooleanField(label=_('查询寝室'), default=False)),
        )



@site
class InClassRoomExcel(ExcelInData):
    name = _('导入白天课堂考勤')

    def get_context(self, request, *args, **kwargs):
        self.init(request)
        user = request.user
        # task, task_t = Task.objects.get_or_create(types='3', college=college)



@site
class BatchAttendance(ExcelInData):
    name = _('批量考勤')
    need_permissions = ('SchoolAttendance.zq_data_import',)
            

    def get_context(self, request, *args, **kwargs):
        user = request.user
        task = Task.objects.get_or_create(types=request.params.task_type, college=user.grade.college)[0]
        rule = models.RuleDetails.objects.get(id = request.params.rule_id)
        self.init(request)

        # 获取所有历史早签记录
        query = Record.objects.filter(task=task, rule=rule).values(
            name=F('student_approved__username'), time=F('star_time')
        )
        db_records = []
        for q in query:
            time = q['time']
            time = str(time.year) + '/' + str(time.month) + '/' + str(time.day)
            name = q['name']
            db_records.append(name + time)


        wait_create_record = []  # 等待批量获取的记录实例
        for row in self.rows:
            username = row['username']
            time = row['time']

            if time == None:
                self.add_error(username,time,'日期不能为空')
                continue

            time = self.time_formatting(time)  
            if (username + time) not in db_records:
                u = self.db_users[username]
                try:
                    star_time = datetime.datetime.strptime(time, '%Y/%m/%d')
                except:
                    self.add_error(username,self.get_name(username),time,'日期格式错误')
                    continue

                wait_create_record.append(Record(
                    rule_str = rule.name,
                    student_approved = u,
                    student_approved_username = u.username,
                    student_approved_name = u.name,
                    score = rule.score,
                    grade_str = u.grade.name,
                    star_time = star_time,
                    worker = user,
                    task = task,
                    rule = rule,
                ))
            else:
                self.add_error(username,self.get_name(username),time,'已经存在')

        Record.objects.bulk_create(wait_create_record)
        return self.error_list

    class Meta:
        param_fields = (
            ('file', fields.FileField(label=_('Excel文件'),default=None)),
            ('rule_id', fields.CharField(label=_('规则id'), default=None)),
            ('task_type', fields.CharField(label=_('任务类型'), default=None)),

        )


@site
class OutData(CoolBFFAPIView,ExcelBase):
    name = _('筛选导出记录情况')

    def get_context(self, request, *args, **kwargs):
        ret = {}
        # 获取用户所属分院
        username = request.params.username
        college_id = request.params.college_id
        start_date = get_start_date(request)
        end_date = get_end_date(request)
        # 筛选条件
        q1 = Q(manager__isnull=True)  # 是否销假
        q2 = Q(star_time__range=(start_date, end_date))  # 时间
        q3 = (
            Q(
                student_approved=User.objects.get(
                    Q(username=username) | Q(name=username)
                )
            )
            if username != None
            else q1
        )  # 是否名称搜索
        q4 = Q(task__types__in=['2', '0', '3'])  # 任务类型限制
        q5 = Q(task__college__id=college_id)  # 分院
        q6 = Q(rule__isnull=False)
        records = (
            models.Record.objects.filter(q2 & q1 & q3 & q4 & q5 & q6 )
            .values(
                grade=F('grade_str'),
                name=F('student_approved__name'),

            )
            .annotate(
                rule=Concat('rule_str'),
                score_onn=Concat('score'),
                score=Sum('score'),
                time=Concat('star_time'),
                rule_type=Concat('rule__rule__codename'),
            )
            .values(
                'grade',
                'name',
                'rule_type',
                'rule',
                'score_onn',
                'score',
                'time',
                usernames=F('student_approved__username'),

            )
        )
        for record in records:
            rule_type_ = record['rule_type'].split(',')
            rule_ = record['rule'].split(',')
            score_onn_ = record['score_onn'].split(',')
            time_ = record['time'].split(',')
            rule_02_time = {}

            if len(time_) != len(rule_):
               record['name'] += ' 异常'

            for index in range(0, len(rule_type_)):
                type_ = rule_type_[index]
                if index > len(time_)-1:
                    break
                if not type_ + 'score' in record:
                    record[RULE_CODE_01 + 'score'] = 0
                    record[RULE_CODE_02 + 'score'] = 0
                    record[RULE_CODE_03 + 'score'] = 0
                    record[RULE_CODE_04 + 'score'] = 0
                    record[RULE_CODE_05 + 'score'] = 0
                    # record[RULE_CODE_07+'score'] = 0
                    record[RULE_CODE_08+'score'] = 0
                    record[RULE_CODE_09+'score'] = 0
                if not type_ + 'rule' in record:
                    record[RULE_CODE_01 + 'rule'] = ''
                    record[RULE_CODE_02 + 'rule'] = ''
                    record[RULE_CODE_03 + 'rule'] = ''
                    record[RULE_CODE_04 + 'rule'] = ''
                    record[RULE_CODE_05 + 'rule'] = ''
                    # record[RULE_CODE_07+'rule'] = ''
                    record[RULE_CODE_08+'rule'] = ''
                    record[RULE_CODE_09+'rule'] = ''

                # 分数累加
                record[type_ + 'score'] += float(score_onn_[index])

                t = time_[index][5:10]
                # 统计晚自修点名扣分
                if type_ == RULE_CODE_02:
                    if t not in rule_02_time.keys():
                        rule_02_time[t] = []
                    rule_02_time[t].append(rule_[index])
                    
                # 规则拼接
                record[type_ + 'rule'] += t + ":" + str(rule_[index]) + '\r\n'
            
            # 计算晚自修点名扣分
            if len(rule_02_time.keys())>0:
                for k in rule_02_time:
                    if len(rule_02_time[k]) == 1:
                        record[RULE_CODE_02 + 'score']+=2
                        record['score']+=2
                        

            rule_str = record[type_ + 'rule']
            record[type_ + 'rule'] = rule_str[0 : len(rule_str) - 2]

            del record['time']
            del record['rule_type']
            del record['rule']
            del record['score_onn']
            
        # 导出
        ws = self.open_excel("/core/file/学生考勤信息记录.xlsx")
        for i in records:
            k = dict(i)
            ws.append([
                k.get('grade',''),
                k.get('usernames',''),
                k.get('name',''),
                # 晨点
                k.get(RULE_CODE_08+'score',0),
                k.get(RULE_CODE_08+'rule',''),
                # 晨跑
                k.get(RULE_CODE_09+'score',0),
                k.get(RULE_CODE_09+'rule',''),
                # 早签
                k.get(RULE_CODE_04+'score',0),
                k.get(RULE_CODE_04+'rule',''),
                # 晚签
                k.get(RULE_CODE_02+'score',0),
                k.get(RULE_CODE_02+'rule',''),
                # 晚自修违纪
                k.get(RULE_CODE_03+'score',0),
                k.get(RULE_CODE_03+'rule',0),
                # 查寝
                k.get(RULE_CODE_01+'score',0),
                k.get(RULE_CODE_01+'rule',''),
                # 课堂
                k.get(RULE_CODE_05+'score',0),
                k.get(RULE_CODE_05+'rule',''),
                k.get('score','')
            ])
        TIME = datetime.datetime.now()#.strftime("%H:%M:%S")
        ws.append(['统计时间:',TIME])
        response = self.create_excel_response('学生缺勤表')
        return self.write_file(response,ws)

    class Meta:
        param_fields = (
            ('username', fields.CharField(label=_('用户名'), default=None)),
            ('college_id', fields.IntegerField(label=_('分院ID'), default=None)),
            ('start_date', fields.DateField(label=_('开始日期'), default=None)),
            ('end_date', fields.DateField(label=_('结束日期'), default=None)),
        )


urls = site.urls
urlpatterns = site.urlpatterns
