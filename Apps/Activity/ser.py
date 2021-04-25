from rest_framework import serializers
from .models import *


class ManageSerializer(serializers.ModelSerializer):
    """查寝记录数据的序列化"""
    college = serializers.SerializerMethodField()

    def get_college(self, value: Manage):
        return value.college.name

    class Meta:
        model = Manage
        fields = ('id', 'types', 'college', 'console_code', 'code_name')


class TaskRecordAntiSerializer(serializers.Serializer):
    """查寝记录反序列化"""

    def create(self, validated_data):
        return TaskRecord.objects.create(**validated_data)

    def update(self, instance: TaskRecord, validated_data: dict):
        instance.task_type = validated_data.get('task_type', instance.task_type)
        instance.worker = validated_data.get('worker', instance.worker)
        instance.student_approved = validated_data.get('student_approved', instance.student_approved)
        instance.manager = validated_data.get('manager', instance.manager)
        instance.score = validated_data.get('score', instance.score)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.reason_str = validated_data.get('reason_str', instance.reason_str)
        instance.last_modify_time = validated_data.get('last_modify_time', instance.last_modify_time)
        instance.grade_str = validated_data.get('grade_str', instance.grade_str)
        instance.save()
        return instance
