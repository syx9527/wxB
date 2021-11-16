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
    email = serializers.CharField(label="邮箱", validators=[email_validator, ], allow_blank=True)
    phone = serializers.CharField(label="手机号", validators=[phone_validator, ])
    id_number = serializers.CharField(label="身份证", validators=[id_number__validator, ])
    is_admin = serializers.CharField(label="用户类别", validators=[is_admin_validator, ])
    openid = serializers.CharField(label="微信标识", )
    name = serializers.CharField(label="真实姓名", )
    native = serializers.CharField(label="籍贯", )
    address = serializers.CharField(label="家庭住址", )
    gender = serializers.CharField(label="性别", validators=[gender_validator, ])
