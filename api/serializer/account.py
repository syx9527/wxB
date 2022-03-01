from rest_framework import serializers

from .validators import *


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    # email = serializers.CharField(label="邮箱", validators=[email_validator, ])


class LoginMessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    # email = serializers.CharField(label="邮箱", validators=[email_validator, ])
    code = serializers.CharField(label="验证码", validators=[code_validator, ])


class LoginSerializer(serializers.Serializer):
    # phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    email = serializers.CharField(label="邮箱", validators=[email_validator, ])
    code = serializers.CharField(label="邮箱", validators=[code_validator, ])


class UserInfoSerializer(serializers.Serializer):
    email = serializers.CharField(label="邮箱", validators=[email_validator, ], allow_blank=True, )
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    # is_admin = serializers.CharField(label="用户类别", validators=[is_admin_validator, ])
    openid = serializers.CharField(label="微信标识", )
    name = serializers.CharField(label="真实姓名", )
    native = serializers.CharField(label="籍贯", )
    address = serializers.CharField(label="家庭住址", )
    gender = serializers.CharField(label="性别", validators=[gender_validator, ])
    avatar_url = serializers.CharField(label="照片地址", )


class ReditUserInfoSerializer(serializers.Serializer):
    email = serializers.CharField(label="邮箱", validators=[email_validator, ], allow_blank=True)
    # phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    is_admin = serializers.CharField(label="用户类别", validators=[is_admin_validator, ])
    openid = serializers.CharField(label="微信标识", )
    name = serializers.CharField(label="真实姓名", )
    native = serializers.CharField(label="籍贯", )
    address = serializers.CharField(label="家庭住址", )
    gender = serializers.CharField(label="性别", validators=[gender_validator, ])


class ForeignWorkersSerializer(serializers.Serializer):
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])

    name = serializers.CharField(label="真实姓名", )
    gender = serializers.CharField(label="性别", validators=[gender_validator, ])
    visiting_reason = serializers.CharField(label="来访事由", )
    openid = serializers.CharField(label="微信标识id", )
    code = serializers.CharField(label="操作码", validators=[code_type_validator])

    # health_code = serializers.FileField(label="健康码")
    # travel_card = serializers.FileField(label="行程卡")
    # cov_report = serializers.FileField(label="核酸检测报告")

    health_code = serializers.CharField(label="健康码")
    # health_code = serializers.FileField(label="健康码")

    travel_card = serializers.CharField(label="行程卡")
    cov_report = serializers.CharField(label="核酸检测报告")


class GetForeignWorkersSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    page = serializers.CharField(label="页码", validators=[is_number], allow_blank=True, )
    size = serializers.CharField(label="每页数据量", validators=[is_number], allow_blank=True)
    status = serializers.CharField(label="status", validators=[status_validator], allow_blank=True, )


class GetEntryAndExitDeclarationSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    page = serializers.CharField(label="页码", )
    size = serializers.CharField(label="每页数据量", )
    status = serializers.CharField(label="status", validators=[status_validator])


class ReForeignWorkersSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    status = serializers.CharField(label="审核员审核状态", validators=[admin_status_validator])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])


class EntryAndExitDeclarationSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    subject_matte = serializers.CharField(label="出入事由", )
    start_time = serializers.CharField(label="起始时间", )
    end_time = serializers.CharField(label="截止时间", )

    health_code = serializers.CharField(label="健康码")
    travel_card = serializers.CharField(label="行程卡")
    cov_report = serializers.CharField(label="核酸检测报告")


class ReEntryAndExitDeclarationSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    status = serializers.CharField(label="审核员审核状态", validators=[en_exit_status_validator])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])


class CheckBaseUserDeclarationSerializer(serializers.Serializer):
    name = serializers.CharField(label="姓名", )
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])


class NewUserCheckOldUserrDeclarationSerializer(serializers.Serializer):
    name = serializers.CharField(label="姓名", )
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    openid = serializers.CharField(label="openid", )


class FindUserSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )


class DelUserSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])


class AuditBasicsUserInfoSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    op = serializers.CharField(label="操作码", validators=[audit_op_validator])


class FindUserByIdNumberSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])


class RedUserByIdNumberSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    status = serializers.CharField(label="审核状态", validators=[admin_status_validator])
    user_type = serializers.CharField(label="人员类型", validators=[user_type_validator])
    reason = serializers.CharField(label="审核理由", allow_blank=True, )


class CheckOpenid(serializers.Serializer):
    openid = serializers.CharField(label="openid", )


class AddCommunity2LigatureSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    name = serializers.CharField(label="名称", )
    category = serializers.CharField(label="类别", validators=[category_validator])
    address = serializers.CharField(label="地址", )
    control_strategy = serializers.CharField(label="管控策略", validators=[control_strategy_validator])


class ReAddCommunity2LigatureSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    uid = serializers.CharField(label="编号", )
    name = serializers.CharField(label="名称", )
    # category = serializers.CharField(label="类别", validators=[category_validator])
    address = serializers.CharField(label="地址", )
    control_strategy = serializers.CharField(label="管控策略", validators=[control_strategy_validator])


class DelCommunity2LigatureSerializer(serializers.Serializer):
    uid = serializers.CharField(label="编号", )
    openid = serializers.CharField(label="openid", )


class FindCommunity2LigatureSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    query = serializers.CharField(label="query", allow_blank=True, )
    category = serializers.CharField(label="类别", allow_null=True, validators=[category_validator])
    page = serializers.CharField(label="页码", allow_null=True, validators=[is_number], default=1)
    size = serializers.CharField(label="每页数据量", allow_null=True, validators=[is_number], default=10)


class AdminFindUserSerializer(serializers.Serializer):
    openid = serializers.CharField(label="openid", )
    query = serializers.CharField(label="query", allow_blank=True, )

    page = serializers.CharField(label="页码", allow_blank=True, allow_null=True, validators=[is_number], default=1)
    is_admin = serializers.CharField(label="is_admin", allow_blank=True, allow_null=True,
                                     validators=[is_admin_validator], default=1)
    size = serializers.CharField(label="每页数据量", allow_blank=True, allow_null=True, validators=[is_number], default=10)


class AdminDelUserSerializer(serializers.Serializer):
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    openid = serializers.CharField(label="openid", )


class AdminReUserSerializer(serializers.Serializer):
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    openid = serializers.CharField(label="openid", )
    ownership = serializers.CharField(label="社区/哨卡 ID", )


class GetCommunityListSerializer(serializers.Serializer):
    category = serializers.CharField(label="类别", allow_blank=True, allow_null=True, validators=[category_validator])


class AdminAddUserSerializer(serializers.Serializer):
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    openid = serializers.CharField(label="openid", )
    ownership = serializers.CharField(label="社区/哨卡ID", )
