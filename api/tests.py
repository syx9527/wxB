import json
import re
import uuid

import requests
from lxml.etree import HTML

# user = BasicsUserInfo.objects.get(id_number="533122199811201414")
# user1 = UserInfo.objects.get(basics_info=user)
# res = AdminUserInfo.objects.create(user_info=user1, admin_id=user.id_number[-6:], admin_post=user.is_admin)
# print(res)
from api.models import Areas

# Create your tests here.
from api.models import *
