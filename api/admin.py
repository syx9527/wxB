from django.contrib import admin

from .models import *

# Register your models here.
"""
class ArticleAdmin(admin.ModelAdmin):
    '''设置列表可显示的字段'''
    list_display = ('title', 'author', 'status', 'mod_date',)

    '''设置过滤选项'''
    list_filter = ('status', 'pub_date',)

    '''每页显示条目数'''
    list_per_page = 5

    '''设置可编辑字段'''
    list_editable = ('status',)

    '''按日期月份筛选'''
    date_hierarchy = 'pub_date'

    '''按发布日期排序'''
    ordering = ('-mod_date',)
"""


class ArticleAdmin(admin.ModelAdmin):
    '''设置列表可显示的字段'''
    list_display = ('title', 'author', 'status', 'mod_date',)

    '''设置过滤选项'''
    list_filter = ('status', 'pub_date',)

    '''每页显示条目数'''
    list_per_page = 5

    '''设置可编辑字段'''
    list_editable = ('status',)

    '''按日期月份筛选'''
    date_hierarchy = 'pub_date'

    '''按发布日期排序'''
    ordering = ('-mod_date',)


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('openid', 'nickName', 'createTime', 'lastTime', 'is_valid', 'basics_info',)
    list_filter = ('is_valid', 'gender',)
    list_per_page = 15
    # list_editable = ('is_valid',)
    # date_hierarchy = 'pub_date'
    ordering = ('is_valid',)


class BasicsUserInfoAdmin(admin.ModelAdmin):
    list_display = ('is_admin', 'name', 'id_number', 'gender', 'ownership', 'status',)
    list_filter = ("name", 'status', 'gender', "ownership")
    list_per_page = 15
    # list_editable = ('is_valid',)
    # date_hierarchy = 'pub_date'
    ordering = ('status',)


class Entry2ExitDeclarationAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'create_time', 'status', 'audit_time', 'is_valid',)
    list_filter = ("user", 'status', "is_valid")
    list_per_page = 15
    # list_editable = ('is_valid',)
    # date_hierarchy = 'pub_date'
    ordering = ('-create_time',)
    date_hierarchy = 'create_time'


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('auditor', 'audit_time', 'audited_user', 'status',)
    list_filter = ("status",)
    list_per_page = 15
    # list_editable = ('is_valid',)
    # date_hierarchy = 'pub_date'
    ordering = ('-audit_time',)


admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Community2LigaturesImgs)
admin.site.register(Community2LigaturesInfo)
admin.site.register(BasicsUserInfo, BasicsUserInfoAdmin)
admin.site.register(AdminUserInfo)
admin.site.register(VaccinationRecord)
admin.site.register(SupportingImgs)
admin.site.register(Entry2ExitDeclaration, Entry2ExitDeclarationAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(TrafficRecord)

admin.site.register(ForeignWorkers)

admin.site.site_header = '微信小程序后台管理'
admin.site.site_title = '微信小程序后台管理'
