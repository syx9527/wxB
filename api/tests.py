# user = BasicsUserInfo.objects.get(id_number="533122199811201414")
# user1 = UserInfo.objects.get(basics_info=user)
# res = AdminUserInfo.objects.create(user_info=user1, admin_id=user.id_number[-6:], admin_post=user.is_admin)
# print(res)

# Create your tests here.

# suer = ForeignWorkers.objects.all()
# for _ in suer:
#     _.is_valid = True
#     _.status = 0
#     _.save()

import random
import time

from .models import *

time
# # 添加外来人员登记
# user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid='test').basics_info.id)
# base_id = "5331221998112012"
# for i in range(63):
#     ForeignWorkers.objects.create(
#         name="test" + "%05d" % i,
#         id_number=base_id + "%02d" % i,
#         phone="176069287" + "%02d" % i,
#         status=0,
#         health_code='foreign_workers/202201120000700566.jpg',
#         travel_card='foreign_workers/202201120000700566.jpg',
#         cov_report='foreign_workers/202201120000700566.jpg',
#         visiting_reason="批量测试" + "%02d" % i,
#         by_user=user,
#     )

start_time = timezone.now()
# for i in range(180):
#     # 添加居民出入申报
#     user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid='test').basics_info.id)
#     # time.sleep(random.randint(2, 7))
#     end_time = timezone.now()
#     status = random.choice((0, 1))
#     audit_time = None
#     if status == 1:
#         audit_time = timezone.now()
#     Entry2ExitDeclaration.objects.create(
#         user=user,
#         subject_matte="出入测试" + "%02d" % i,
#         end_time=end_time,
#         start_time=start_time,
#         health_code='foreign_workers/202201120000700566.jpg',
#         travel_card='foreign_workers/202201120000700566.jpg',
#         cov_report='foreign_workers/202201120000700566.jpg',
#         is_valid=False,
#         status=status,
#         audit_time=audit_time
#     )
#     print(i)
#
# _ = Entry2ExitDeclaration.objects.filter(status=0, is_valid=False)
# for user in _:
#     user.status = -1
#     user.save()
#
# _ = Entry2ExitDeclaration.objects.filter(status=-1, audit_time=None)
# for user in _:
#     user.audit_time = timezone.now()
#     user.save()
#
# _ = Entry2ExitDeclaration.objects.all().first()
# _.status = 0
# _.is_valid = True
# _.save()


try:
    for i in range(1, 10):
        Community2LigaturesInfo.objects.create(uid="00%s" % i, name="%s社区" % i, category=1, address="xx省",
                                               control_strategy=random.randint(0, 3))

    ownership = Community2LigaturesInfo.objects.filter(category=1).first()
    test_user = BasicsUserInfo.objects.create(is_admin=1, name='test', id_number='533122199811201414', native='云南',
                                              address="云南", phone="17606927841", email="12@q.com", status=1,
                                              ownership=ownership)
    UserInfo.objects.create(openid='test', nickName="test", basics_info=test_user)

    admin_user = BasicsUserInfo.objects.create(is_admin=2, name='admin', id_number='533122199811201415', native='云南',
                                               address="云南", phone="17606927842", email="12@q.com", status=1,
                                               ownership=ownership)
    UserInfo.objects.create(openid='admin', nickName="admin", basics_info=admin_user)

    AdminUserInfo.objects.create(user_info=admin_user, admin_id="A001", admin_ownership=ownership,
                                 admin_post=admin_user.is_admin)

except:
    pass
