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

from .models import *

user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid='test').basics_info.id)
base_id = "5331221998112012"
for i in range(63):
    ForeignWorkers.objects.create(
        name="test" + "%05d" % i,
        id_number=base_id + "%02d" % i,
        phone="176069287" + "%02d" % i,
        status=0,
        health_code='foreign_workers/202201120000700566.jpg',
        travel_card='foreign_workers/202201120000700566.jpg',
        cov_report='foreign_workers/202201120000700566.jpg',
        visiting_reason="批量测试" + "%02d" % i,
        by_user=user,
    )
