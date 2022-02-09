'''
Author: 邹洋
Date: 2021-05-20 08:37:12
Email: 2810201146@qq.com
LastEditors:  
LastEditTime: 2022-02-07 15:08:39
Description: 
'''
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import *
from django.utils.html import format_html

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """任务管理"""
    list_display = (
        "id", "college", "types", "is_open"
    )
    # filter_horizontal = ("admin","buildings","grades")

class CountryFilter(SimpleListFilter):
    title = '是否查询销假人' # or use _('country') for translated title
    parameter_name = '是否查询销假人'

    def lookups(self, request, model_admin):
        return [(1, '否'), (2, '是')]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(manager_username__isnull=True)
        elif value == '2':
            return queryset.filter(manager_username__isnull=False)


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    """考勤记录"""
    list_display = (
        "id", "task","rule_str","score","grade_str","room_str",
        "student_approved_username","student_approved_name",
        "worker_username","worker_name","manager_username","manager_name", "star_time","last_time",
    )
    list_filter = ("task__types","rule__rule__name","rule__name","grade_str","room_str",CountryFilter)
    # list_editable =("rule_str","score")
    date_hierarchy = 'star_time'

    search_fields = ("student_approved_username","student_approved_name","manager_username","manager_name")
    actions = ['batch_pin','batch_pin_cancel',]

    def batch_pin(self, request, queryset):
        flag = True
        for i in queryset:
            if i.manager_username:
                self.message_user(request, '已经有人被销假了，无法批量销假！！')
                flag = False
                break
            else:
                continue
        if flag:
            for q in queryset:
                q.manager_username  = request.user.username
                try:
                    q.manager_name  = request.user.last_name + request.user.first_name
                except:
                    self.message_user(request, '销假失败：管理员名称为空')
                    return
                q.save()
            self.message_user(request, '批量销假成功！！')

    batch_pin.short_description = '批量销假'

    def batch_pin_cancel(self, request, queryset):
        if request.user:
            queryset.update(manager_username=None,manager_name=None)
            self.message_user(request, '批量取消成功！！')

    batch_pin_cancel.short_description = '批量取消销假'

    # 添加自定义按钮
    def perator(self,  request, queryset):
        html = '<h1> Hello World </h1>'
        # return HttpResponse(html, status=200)
        # return render(request, 'a.html',{})
        pass
    perator.short_description = format_html("""<a target='_self'  href='/api/school_attendance/a' style="position: relative;left: -12px;">本窗口查看</a>""")