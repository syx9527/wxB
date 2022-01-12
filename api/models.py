import django.utils.timezone as timezone
from django.db import models


# Create your models here.

class UserLog(models.Model):
    user_id = models.ForeignKey(to="UserInfo", to_field='id', on_delete=models.CASCADE)
    obj_name = models.CharField(verbose_name="操作名称", max_length=128, null=False)
    obj_time = models.DateTimeField(verbose_name="操作记录时间", auto_now=True)


class Image(models.Model):
    """图片"""
    openid = models.ForeignKey(to="UserInfo", to_field='id', on_delete=models.CASCADE)

    img_name = models.CharField(max_length=252, default="", verbose_name="文件名")
    img_md5 = models.CharField(max_length=128, verbose_name="MD5值")
    img_type = models.CharField(max_length=32, verbose_name="类型")
    img_size = models.IntegerField(verbose_name="图片大小")
    img_path = models.CharField(max_length=128, verbose_name="图片在服务器保存的路径")
    img_url = models.CharField(max_length=128, default='', verbose_name="图片访问url")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_image'
        verbose_name = '图片信息'
        verbose_name_plural = verbose_name


"""
开始

"""


class Community2LigaturesImgs(models.Model):
    """
    社区/哨卡图片
    """
    img = models.ImageField(upload_to='community&ligatures/', verbose_name='图片地址')

    name = models.ForeignKey(verbose_name="所属社区", to="Community2LigaturesInfo", on_delete=models.CASCADE)

    # single = models.CharField(max_length=256, null=True, blank=True, verbose_name='图片名称', default=name.name)

    def __str__(self):
        return str(self.name.name)

    class Meta:
        verbose_name = verbose_name_plural = "社区/哨卡图片"


class Community2LigaturesInfo(models.Model):
    """
    社区/哨卡基本信息
    """
    CONTROL_STRATEGY_STATUS = (
        (0, "不允许进出"),
        (1, "只进不出"),
        (2, "只出不进"),
        (3, "无"),
    )

    CATEGORY = (

        (1, "社区"),
        (2, "哨卡"),
    )
    id_number = models.CharField(verbose_name="编号", max_length=24, null=False, blank=False, default="", unique=True)
    name = models.CharField(verbose_name="社区/哨卡名称", max_length=128, null=False, blank=False, default="")
    category = models.IntegerField(verbose_name="类别", choices=CATEGORY, )
    address = models.CharField(verbose_name="地址", max_length=256, null=False, blank=False, default="")
    control_strategy = models.IntegerField(verbose_name="管控策略", choices=CONTROL_STRATEGY_STATUS, default=3)

    # photos = models.ManyToManyField(Community2LigaturesImgs, related_name='imgs', verbose_name='社区/哨卡图片', null=True,
    #                                 blank=True)

    class Meta:
        verbose_name = verbose_name_plural = "社区/哨卡基本信息"

    def __str__(self):
        return self.name


class BasicsUserInfo(models.Model):
    """
    用户基本信息
    """
    IS_ADMIN_CHOICES_STATUS = (
        (0, "待选择"),
        (1, "社区居民"),
        (2, "网格员"),
        (3, "哨卡员"),
        (4, "审核员"),
        (5, "超级管理员"),
    )

    STATUS = (

        (0, "待审核"),
        (1, "审核通过"),
        (2, "审核失败"),
    )
    GENDER = (
        (1, "男"),
        (0, "女"),
    )

    is_admin = models.IntegerField(verbose_name="用户类别", choices=IS_ADMIN_CHOICES_STATUS, default=0)
    name = models.CharField(verbose_name="姓名", max_length=12, null=False, blank=False, default="")
    id_number = models.CharField(verbose_name="身份证号码", max_length=18, null=False, blank=True, default="", unique=True)
    native = models.CharField(verbose_name="籍贯", max_length=128, null=False, blank=True, default="")
    address = models.TextField(verbose_name="家庭住址", null=False, blank=True, default="")
    phone = models.CharField(verbose_name="手机号码", max_length=11, default="", null=True, blank=True, unique=True)
    email = models.EmailField(verbose_name="电子邮箱", default="", null=True, blank=True)
    status = models.IntegerField(verbose_name="审核状态", choices=STATUS, default=0)
    gender = models.IntegerField(verbose_name="性别", choices=GENDER, null=False, blank=True, default=1)
    ownership = models.ForeignKey(to="Community2LigaturesInfo", null=False, blank=False, verbose_name="所属网格/哨卡",
                                  default=None, on_delete=models.CASCADE)

    class Meta:
        verbose_name = verbose_name_plural = "用户基本信息"

    def __str__(self):
        return self.name


class Car(models.Model):
    """
    车辆信息
    """
    user = models.ManyToManyField(verbose_name="车主", to=BasicsUserInfo)
    carNo = models.CharField(verbose_name="车牌", max_length=10, null=False, blank=False, unique=True)
    type = models.CharField(verbose_name="类型", max_length=10, null=False, blank=False)
    color = models.CharField(verbose_name="颜色", max_length=10, null=False, blank=False)


class UserInfo(models.Model):
    """
    微信用户基本信息
    """
    GENDER = (
        (1, "男"),
        (0, "女"),
    )
    openid = models.CharField(verbose_name="ID", max_length=128, null=False, blank=True, unique=True)
    nickName = models.CharField(verbose_name="用户名", max_length=32, null=True, blank=True, default=None)
    email = models.EmailField(verbose_name="邮箱", max_length=64, null=True, blank=True, default=None)
    phone = models.CharField(verbose_name="电话", null=True, blank=True, default=None, max_length=24)
    gender = models.IntegerField(verbose_name="性别", choices=GENDER, null=True, blank=True, default=1)
    language = models.CharField(verbose_name="语言", max_length=32, null=True, blank=True, default=None)
    city = models.CharField(verbose_name="城市", max_length=32, null=True, blank=True, default=None)
    province = models.CharField(verbose_name="省份", max_length=32, null=True, blank=True, default=None)
    country = models.CharField(verbose_name="国家", max_length=32, null=True, blank=True, default=None)
    avatarUrl = models.URLField(verbose_name="头像", null=True, blank=True, default=None)
    createTime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, )
    lastTime = models.DateTimeField(verbose_name="最后登录时间", auto_now=True, )
    is_valid = models.BooleanField(verbose_name="是否有效(没被注销)", default=True)
    basics_info = models.OneToOneField(verbose_name="对应用户", to="BasicsUserInfo", blank=True, on_delete=models.SET_NULL,
                                       null=True)

    class Meta:
        verbose_name = verbose_name_plural = "微信用户基本信息"

    def __str__(self):
        return self.nickName

    def delete(self, *args, **kwargs):
        if self.basics_info:
            _ = BasicsUserInfo.objects.get(id=self.basics_info.id)
            _.delete()
        return super().delete(*args, **kwargs)


class AdminUserInfo(models.Model):
    """
    网格/哨卡员/审核员信息
    """
    POST = (
        (2, "网格员"),
        (3, "哨卡员"),
        (4, "审核员"),
    )

    user_info = models.OneToOneField(to="BasicsUserInfo", to_field="id", on_delete=models.DO_NOTHING, null=False)
    admin_id = models.CharField(verbose_name="编号", max_length=24, null=False, blank=False, unique=True)
    admin_ownership = models.ForeignKey(to="Community2LigaturesInfo", verbose_name="所属网格/哨卡", on_delete=models.CASCADE)
    admin_post = models.IntegerField(verbose_name="职务", choices=POST, default=2)

    class Meta:
        verbose_name = verbose_name_plural = "网格/哨卡员/审核员信息"

    def __str__(self):
        return self.user_info.name


class VaccinationRecord(models.Model):
    """
    疫苗接种记录
    """
    user_id = models.ManyToManyField(to="BasicsUserInfo", )
    inoculant_times = models.IntegerField(verbose_name="接种次数", null=False, blank=False, default=0)
    inoculant_datetime = models.DateTimeField(verbose_name="接种日期", null=False, blank=False, default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = "疫苗接种记录"

    def __str__(self):
        return self.user_id.name


class SupportingImgs(models.Model):
    """
    证明材料
    """
    UPLOAD_TO = "supporting_materials/"
    img = models.ImageField(upload_to=UPLOAD_TO, verbose_name='证明材料')
    for_declaration = models.ForeignKey(verbose_name="申报", to="Entry2ExitDeclaration", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.for_declaration.user.name)

    class Meta:
        verbose_name = verbose_name_plural = "证明材料"


class Entry2ExitDeclaration(models.Model):
    """
    出入申报
    """
    STATUS = (
        (-1, "审核失败"),
        (0, "待审核"),
        (1, "审核成功"),
    )
    UPLOAD_TO = "entry_exit/"
    user = models.ForeignKey(verbose_name="社区居民", to="BasicsUserInfo", on_delete=models.CASCADE)
    subject_matte = models.CharField(verbose_name="出入事由", max_length=128, null=False, blank=False, default="")
    start_time = models.DateTimeField(verbose_name="开始时间", null=False, blank=False, default=timezone.now)
    end_time = models.DateTimeField(verbose_name="截至时间", null=False, blank=False, default=timezone.now)
    health_code = models.ImageField(verbose_name="健康吗", null=False, blank=False, upload_to=UPLOAD_TO)
    travel_card = models.ImageField(verbose_name="行程卡", null=False, blank=False, upload_to=UPLOAD_TO)
    cov_report = models.ImageField(verbose_name="核酸检测报告", null=False, blank=False, upload_to=UPLOAD_TO)
    status = models.IntegerField(verbose_name="审核状态", choices=STATUS, default=0)
    is_valid = models.BooleanField(verbose_name="是否处于有效期", default=True, null=False, blank=False)
    create_time = models.DateTimeField(verbose_name="申报时间", auto_now_add=True)
    audit_time = models.DateTimeField(verbose_name="审核时间", null=True, blank=False, default=None)


    def __str__(self):
        return self.user.name

    class Meta:
        verbose_name = verbose_name_plural = "出入申报"


class AuditLog(models.Model):
    """
    人员出入审核记录表
    """

    STATUS = (
        (1, "审核通过"),
        (-1, "审核失败"),
    )
    auditor = models.ForeignKey(verbose_name='审核员', to="AdminUserInfo", on_delete=models.DO_NOTHING)
    audit_time = models.DateTimeField(verbose_name="审核时间", null=False, blank=False, auto_now=True)
    audit_user = models.ForeignKey(verbose_name='居民', to="BasicsUserInfo", on_delete=models.DO_NOTHING, null=True)
    result = models.IntegerField(verbose_name="审核结果", choices=STATUS, default=1)

    def __str__(self):
        return self.auditor.user_info.name

    class Meta:
        verbose_name = verbose_name_plural = "人员审核记录表"


class TrafficRecord(models.Model):
    """
    通行记录
    """
    UPLOAD_TO = "trajectory_diagram/"
    person_name = models.ManyToManyField(to="BasicsUserInfo", )
    address_names = models.ManyToManyField(to="Community2LigaturesInfo")  # 建立多对多关系，将卡点或者社区信息绑定至通行记录中
    data_time = models.DateTimeField(auto_now=True, verbose_name="记录时间")
    trajectory_diagram = models.ImageField(verbose_name="轨迹图", upload_to=UPLOAD_TO)

    # def __str__(self):
    #     return self.person_name

    class Meta:
        verbose_name = verbose_name_plural = "通行记录"


class ForeignWorkers(models.Model):
    """
    外来人员基本信息
    """
    STATUS = (

        (0, "待审核"),
        (1, "审核通过"),
        (2, "审核失败"),
    )
    GENDER = (
        (1, "男"),
        (0, "女"),
    )
    UPLOAD_TO = "foreign_workers/"

    name = models.CharField(verbose_name="姓名", max_length=12, null=False, blank=False, default="")
    gender = models.IntegerField(verbose_name="性别", choices=GENDER, null=False, blank=True, default=1)
    id_number = models.CharField(verbose_name="身份证号码", max_length=18, null=False, blank=True, default="", )
    phone = models.CharField(verbose_name="手机号码", max_length=11, default="", null=True, blank=True, )
    status = models.IntegerField(verbose_name="审核状态", choices=STATUS, default=0)
    health_code = models.ImageField(verbose_name="健康码", upload_to=UPLOAD_TO, )
    travel_card = models.ImageField(verbose_name="行程卡", upload_to=UPLOAD_TO, )
    cov_report = models.ImageField(verbose_name="核酸检测报告", upload_to=UPLOAD_TO, )
    visiting_reason = models.CharField(verbose_name="来访事由", max_length=256, null=False, default='')
    by_user = models.ForeignKey(verbose_name="发起人", to="BasicsUserInfo", on_delete=models.CASCADE)
    is_valid = models.BooleanField(verbose_name="是否处于有效期", default=True, null=False, blank=False)
    create_time = models.DateTimeField(verbose_name="登记时间", auto_now_add=True)
    audit_time = models.DateTimeField(verbose_name="审核时间", null=True, blank=False, default=None)

    class Meta:
        verbose_name = verbose_name_plural = "外来人员登记"

    def save(self, *args, **kwargs):
        if self.status == 2:
            self.is_valid = False
        super().save()

    def __str__(self):
        return self.name


class Areas(models.Model):
    name = models.CharField(max_length=50, verbose_name='地名')
    pid = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='addinfo', null=True, blank=True,
                            verbose_name='上一级别的行政区的id', default=None)

    # on_delete = models.CASCADE # 删除关联数据的时候，与之相关联的也删除
    # on_delete = models.DO_NOTHING # ... , 什么操作也不做
    # on_delete = models.PROTECT # ... ,引发报错
    # on_delete = models.SET_NULL # ... ,设置为空
    # on_delete = models.SET_DEFAULT # ... , 设置为默认值
    # on_delete = models.SET # ... , 删除关联数据

    class Meta:
        db_table = 'areas'

    def __str__(self):
        return self.name


class ImgUpload(models.Model):
    UPLOAD_TO = "temp/"
    # img = models.ImageField(verbose_name="图片", upload_to="temp/")
    img = models.ImageField(verbose_name="图片", upload_to=UPLOAD_TO, unique=False)
    update_time = models.DateTimeField(verbose_name="上传时间", auto_now=True)
    is_valid = models.BooleanField(default=True)


class AutoImgName(models.Model):
    # op=models.Field

    class Meta:
        db_table = 'id_number'

    def __str__(self):
        return self.id
