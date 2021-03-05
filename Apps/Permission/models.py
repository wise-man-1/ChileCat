"""授权数据模型"""
from django.db import models
from django.contrib.auth.models import Permission


# Create your models here.

class ApiPermission(models.Model):
    """接口访问权限"""

    is_verify = models.BooleanField(verbose_name="接口类型", choices=(
        (False, "权限接口"),
        (True, "公开接口"),
    ), default=False)
    
    is_auth = models.BooleanField(verbose_name="登录验证",choices=(
        (False,"不验证"),
        (True,"验证"),
    ))
    permission = models.OneToOneField(
        Permission, on_delete=models.CASCADE,
        verbose_name="权限",
        related_name="api_permission",
        null=True,
        blank=True
    )

    class Meta:
        """Meta definition for ApiPermission."""

        verbose_name = 'API权限'
        verbose_name_plural = 'API权限'

    def __str__(self):
        """Unicode representation of ApiPermission."""
        return self.permission.name


class ElementPermission(models.Model):
    """元素显示权限"""

    name = models.CharField(max_length=50, verbose_name="名称")
    per_id = models.OneToOneField(
        Permission, on_delete=models.CASCADE,
        verbose_name="权限",
        related_name="element_permission"
    )

    class Meta:
        """Meta definition for ElementPermission."""

        verbose_name = 'ElementPermission'
        verbose_name_plural = '元素显示权限'

    def __str__(self):
        """Unicode representation of ElementPermission."""
        return self.name


class OperatePermission(models.Model):
    """操作权限"""

    permission = models.OneToOneField(
        Permission,
        on_delete=models.CASCADE,
        verbose_name="权限",
        related_name="operate_permission"
    )

    class Meta:
        """Meta definition for OperatePermission."""

        verbose_name = '操作权限记录'
        verbose_name_plural = '操作权限记录'

    def __str__(self):
        """Unicode representation of OperatePermission."""
        return self.permission.name


class WriteList(models.Model):
    """白名单."""

    name = models.CharField(max_length=150, verbose_name="内容")
    flag = models.CharField(max_length=20, verbose_name="类型")

    class Meta:
        """Meta definition for WriteList."""

        verbose_name = 'WriteList'
        verbose_name_plural = 'WriteLists'

    def __str__(self):
        """Unicode representation of WriteList."""
        return self.name