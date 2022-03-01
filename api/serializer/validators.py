import re

from rest_framework.exceptions import ValidationError


def phone_validator(value):
    if not re.match(r"^1[3|4|5|6|7|8|9]\d{9}$", value):
        raise ValidationError("手机号错误！")


def is_admin_validator(value):
    if not re.match(r"^(0|1|2|3|4|5)$", value):
        raise ValidationError("用户类别错误！")


def gender_validator(value):
    if not re.match(r"^(0|1)$", value):
        raise ValidationError("用户类别错误！")


def code_type_validator(value):
    if not re.match(r"^(0|1)$", value):
        raise ValidationError("操作码错误！")


def audit_basics_user_op_validator(value):
    if not re.match(r"^(1|2)$", value):
        raise ValidationError("操作码错误！")


def audit_op_validator(value):
    if not re.match(r"^(1|-1)$", value):
        raise ValidationError("操作码错误！")


def id_number__validator(value):
    if not re.match(r"^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$",
                    value):
        raise ValidationError("身份证号错误！")


def code_validator(value):
    if not re.match(r"^\d{4}$", value):
        raise ValidationError("验证码错误！")


def email_validator(value):
    if not re.match(r"^[a-zA-Z0-9_.-]+\@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$", value):
        raise ValidationError("邮箱错误！")


def status_validator(value):
    if not re.match(r"^(3|-1|1|0)$", value):
        raise ValidationError("状态码错误")


def admin_status_validator(value):
    if not re.match(r"^(-1|1)$", value):
        raise ValidationError("状态码错误")


def user_type_validator(value):
    if not re.match(r"^(2|1)$", value):
        raise ValidationError("状态码错误")


def en_exit_status_validator(value):
    if not re.match(r"^(-1|1)$", value):
        raise ValidationError("状态码错误")


def category_validator(value):
    if not re.match(r"^(2|1)$", value):
        raise ValidationError("社区/哨卡类别错误")


def admin_post_validator(value):
    if not re.match(r"^(2|3|4|5)$", value):
        raise ValidationError("管理人员类别错误")


def control_strategy_validator(value):
    if not re.match(r"^(0|1|2|3)$", value):
        raise ValidationError("社区/哨卡管控策略错误")


def is_number(value):
    if not re.match(r"^\d+$", value):
        raise ValidationError("WARNING:this value must is number or null!")
