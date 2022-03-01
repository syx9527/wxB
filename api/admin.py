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
    list_display = ['name', 'id_number', 'gender', 'is_admin', 'ownership', 'status', ]
    list_filter = ("name", 'status', 'gender', "ownership")
    list_per_page = 15
    # list_editable = ('is_valid',)
    # date_hierarchy = 'pub_date'
    ordering = ('status',)
    readonly_fields = ('is_admin', "create_time", "born", 'ownership')
    # readonly_fields = ( "create_time", "born",  'ownership')


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


class AdminUserInfoAdmin(admin.ModelAdmin):
    list_display = ('admin_id', "name", "id_number", 'phone', 'admin_ownership', "is_admin", "create_time",)

    list_filter = ("name", "is_admin", 'admin_ownership',)
    list_editable = ('admin_ownership',)
    search_fields = ("name", "phone", "id_number")  # 搜索字段

    fields = ("user_info", 'admin_ownership', "is_admin", 'admin_id', "name", "id_number", 'phone', "create_time",)

    list_per_page = 15
    # list_editable = ('is_valid',)
    # date_hierarchy = 'pub_date'
    ordering = ('-create_time',)
    readonly_fields = ('admin_id', "create_time", "name", "id_number", "phone",)


class ForeignWorkersAdmin(admin.ModelAdmin):
    list_display = ("name", "id_number", 'phone', "gender", 'status', "visiting_reason", "enter_status",)
    list_display_links = ("name", "id_number", 'phone',)
    fields = ()
    # list_filter = ("name", "is_admin", 'admin_ownership',)
    # list_editable = ('admin_ownership',)
    # search_fields = ("name", "phone", "id_number")  # 搜索字段
    #
    # fields = ("user_info", 'admin_ownership', "is_admin", 'admin_id', "name", "id_number", 'phone', "create_time",)
    #
    # list_per_page = 15
    # # list_editable = ('is_valid',)
    # # date_hierarchy = 'pub_date'
    # ordering = ('-create_time',)
    readonly_fields = ('audit_time', "create_time", "gender", "status")


# class Community2LigaturesInfoAdmin(admin.ModelAdmin):
#     # def type_show(self, obj):
#     #     return [bt.img for bt in obj.photos.all()]
#
#     # fieldsets = (
#     #     (None, {'fields': ('name', 'photos')}),
#     # )
#     # filter_horizontal = ('photos',)
#     # list_display = ['uid', 'name', 'category', 'address', 'control_strategy', 'type_show']
#     list_display = ['uid', 'name', 'category', 'address', 'control_strategy', ]


class StationInLine(admin.StackedInline):
    model = Community2LigaturesImgs
    fields = ('img',)
    # formset = StationFormSet
    extra = 1  # 初始数据量


@admin.register(Community2LigaturesInfo)
class Community2LigaturesInfoAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', "category", 'address', "control_strategy")
    list_display_links = ('uid', 'name',)
    fields = ("uid", "category", 'name', "address", "control_strategy")
    readonly_fields = ('uid',)

    inlines = [StationInLine, ]


admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Community2LigaturesImgs)

# admin.site.register(Community2LigaturesInfo, Community2LigaturesInfoAdmin)

admin.site.register(BasicsUserInfo, BasicsUserInfoAdmin)
admin.site.register(AdminUserInfo, AdminUserInfoAdmin)
# admin.site.register(Community2LigaturesImg)
admin.site.register(VaccinationRecord)
# admin.site.register(SupportingImgs)
admin.site.register(Entry2ExitDeclaration, Entry2ExitDeclarationAdmin)
# admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(TrafficRecord)

admin.site.register(ForeignWorkers, ForeignWorkersAdmin)
# admin.site.register(AdminUserInfo)

admin.site.site_header = '微信小程序后台管理'
admin.site.site_title = '微信小程序后台管理'
