# Create your views here.
# from rest_framework.response import JsonResponse
import json
import logging
import random
import uuid

import django_redis
import requests
from django.conf import settings
from django.core import serializers
from django.core.cache import cache
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import *
from api.serializer.account import LoginMessageSerializer, LoginSerializer, MessageSerializer, UserInfoSerializer
from api.utils import PictureStorageToolClass
from imageserver.utils import conf
from imageserver.utils.api_response import APIResponse

logger = logging.getLogger('django')


class Message(APIView):
    def get(self, request, *args, **kwargs):
        """
        发送手机
        :return:data = {"status": status, "message": message}
        """
        data = {"status": False, }
        # 1.获取手机号（邮箱）

        phone = request.GET.get("phone")
        # print(request.GET)

        # 2.手机格式校验，由于短信验证收费，开发测试采用邮箱验证
        ser = MessageSerializer(data=request.GET)
        if not ser.is_valid():
            return Response(data)
        if cache.get(phone):
            print(cache.get(phone))
            data["code"] = cache.get(phone)
            data["message"] = "验证码5分钟有效！"
            return Response(data)

        # 3.生成随机验证码
        random_code = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(
            random.randint(0, 9))
        # 4.验证码发送到手机上,购买短信服务，阿里云/腾讯云短信
        # TODO tencent.sent_message(phone,random_code)
        # 发送邮箱验证码
        try:
            # message_status = send_mail(subject="验证码", message=f"欢迎您注册，您的验证码为：\n{random_code}\n有效时间为5分钟",
            #                            from_email=settings.EMAIL_HOST_USER, recipient_list=[email], )
            message_status = True
        except:
            message_status = False

        #  验证码发送，发送成功存入数据库
        if message_status:
            print(random_code)
            cache.set(phone, random_code, 60 * 5)  # 设置有效时长，单位  秒
            data["status"] = True
            data["message"] = "验证码发送成功！"
            data["code"] = random_code
        else:
            data["message"] = "验证码发送失败！"
        return Response(data)


class LoginByPhone(APIView):
    """
    手机登录验证
    :return
    status=True,则为新用户
    status=False：
        若无data则验证码错误，有则是登录成功并返回用户个人信息以及openid
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False, }
        phone = request.data.get("phone")
        code = request.data.get("code")

        ser = LoginMessageSerializer(data=request.data)
        if not ser.is_valid():
            return Response(data)

        redis_code = cache.get(phone)
        if code == redis_code:
            try:
                user = BasicsUserInfo.objects.get(phone=phone)
                openid = UserInfo.objects.get(basics_info=user).openid
                res = model_to_dict(user)

                res["openid"] = openid
                data["data"] = res
                return Response(data)

            except:
                data["status"] = True

        return Response(data)


class GetCode2Session(APIView):

    def post(self, request, *args, **kwargs):
        """
        获取用户唯一标识
        :return: openid
        """
        data = {
            "static": False,
        }

        js_code = request.data.get("js_code")

        grant_type = settings.GRANT_TYPE

        # appId = "wxafe035d3c21ea4ef"
        # secret = "2b8b42cdce57e83bfdcfb3b21fe9b857"

        appId = settings.APPID
        secret = settings.SECRET
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={secret}&js_code={js_code}&grant_type={grant_type}"

        response = requests.get(url=url)
        response = json.loads(response.text)
        print("response", response)
        openid = response.get("openid")

        # 返回用户绑定的电话号码
        try:
            user = UserInfo.objects.get(openid=openid)
            phone = user.basics_info.phone
            data['phone'] = phone
        except:
            data['phone'] = None

        if openid:
            data['static'] = True
        data['openid'] = openid

        return Response(data)


class UpdateUser(APIView):
    """
    微信登录
    """

    def post(self, request, *args, **kwargs):
        userInfo = request.data
        print("userInfo", userInfo)
        nickName = userInfo.get("nickName")
        gender = userInfo.get("gender")
        language = userInfo.get("language")
        city = userInfo.get("city")
        province = userInfo.get("province")
        country = userInfo.get("country")
        avatarUrl = userInfo.get("avatarUrl")
        openid = userInfo.get("openid")

        data = {"status": True, }
        try:
            user = UserInfo.objects.get(openid=openid)
            # print("basics_info", user.basics_info.id)
            if user.basics_info:
                data["status"] = False
                user = BasicsUserInfo.objects.get(id=user.basics_info.id)
                res = model_to_dict(user)
                data["data"] = res
        except:
            # user = BasicsUserInfo.objects.filter(idNumber=533122199811201414).first()
            # user = UserInfo.objects.create(openid=openid, basics_info=user)
            user = UserInfo.objects.create(openid=openid)
            # UserLog.objects.create(user_id=user, obj_name="create new user")

            # return Response(data)

            user.nickName = nickName
            user.gender = gender
            user.language = language
            user.city = city
            user.province = province
            user.country = country
            user.avatarUrl = avatarUrl
            user.save()

        # 增加日志记录
        # UserLog.objects.create(user_id=user, obj_name="user login")
        print("data", data)
        return Response(data)


class UpdateUserInfo(APIView):
    """
    完善个人信息,更新个人信息，外来人员登记
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False, }
        userInfo = request.data

        ser = UserInfoSerializer(data=userInfo)

        id_number = userInfo.get("id_number")
        # 验证身份证，电话号码，性别，邮箱，用户类别的合法性,并校验
        if id_number:
            if not ser.is_valid():
                # data["msg"] = {}
                # print(ser.errors)
                for k, v in ser.errors.items():
                    data['msg'] = {}
                    data['msg'][k] = v[0]
                    # print(k, v[0])
                data["code"] = 0
                print("data", data)
                return Response(data)
        openid = userInfo.get("openid")
        is_admin = int(userInfo.get("is_admin"))
        name = userInfo.get("name")

        id_number = id_number.upper()  # 身份证最后若为X,将用户x转换为大写X
        native = userInfo.get("native")
        address = userInfo.get("address")
        phone = userInfo.get("phone")
        email = userInfo.get("email")
        ownership = userInfo.get("ownership")
        gender = int(userInfo.get("gender"))

        user_obasics_info = UserInfo.objects.get(openid=openid)
        status = 0
        if is_admin == 1 | is_admin == 2:
            status = 1
        try:

            user = BasicsUserInfo.objects.create(is_admin=is_admin, name=name, id_number=id_number, native=native,
                                                 address=address, phone=phone, email=email, gender=gender,
                                                 status=status, ownership=ownership)
            user_obasics_info.basics_info = user
            user_obasics_info.save()
        except:
            if not user_obasics_info.basics_info:
                data["code"] = -1
                print("data", data)
                return Response(data)
            user = BasicsUserInfo.objects.get(id_number=id_number)
            # user.phone = phone
            user.email = email
            user.address = address
            user.save()

        data["status"] = True
        data["user_status"] = user.status

        print("data", data)
        return Response(data)


class AuditList(APIView):
    """
    获取审核表(未审核)
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False, "data": []}
        print(request.GET)
        openid = request.GET.get("openid")
        # code = request.GET.get("code")
        code = 0

        page = request.GET.get("page")
        if not page:
            page = 1
        else:
            page = int(page)
        size = request.GET.get("size")
        if not size:
            size = 10
        else:
            size = int(size)

        try:
            AdminUserInfo.objects.get(user_info__userinfo__openid=openid, admin_post=5)
        except:
            return Response(data)

        response_list = BasicsUserInfo.objects.filter(status=code)
        if response_list.exists():
            paginator = Paginator(response_list, size)
            count = paginator.num_pages
            if page > count:
                page = 1
            contacts = paginator.page(page).object_list
            son_data = serializers.serialize("python", contacts, ensure_ascii=False)

            son_data = [i.get("fields") for i in son_data]
            data['data'] = son_data
            data['count'] = count
            data['page'] = page
            data['status'] = True

        # a=json.loads(json.dumps(son_data))
        # print(type(a))
        print(data)
        return Response(data)


class AuditLog(APIView):
    """
    人员信息审核记录
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False, "data": []}
        print(request.GET)
        openid = request.GET.get("openid")
        return Response(data)


class UserExit(APIView):
    def post(self, request, *args, **kwargs):
        openid = request.data.get("openid")

        UserLog.objects.create(user_id=UserInfo.objects.get(openid=openid, ), obj_name="user logout")
        data = {"status": True, "data": None}
        return Response(data)


class Test(APIView):
    def get(self, request, *args, **kwargs):
        data = {"status": True, "data": "666"}
        return Response(data)


class TokenAPIView(GenericAPIView):
    """获取token"""
    authentication_classes = []

    def get(self, request):
        # user_id = request.user.id
        user_id = 1

        # token为uuid
        token = str(uuid.uuid4())
        # 将token保存到redis中
        redis_conn = django_redis.get_redis_connection('token')
        redis_conn.setex('image_token_{}'.format(user_id), conf.TOKEN_TIME, token)

        return APIResponse(data=token, data_msg="获取成功")


class UploadingImageAPIView(GenericAPIView):
    """上传图片"""
    authentication_classes = []

    def post(self, request):

        # user_id = request.user.id
        user_id = 1

        token = request.data.get('token', None)
        image = request.FILES.get('image', None)
        folder = request.data.get('folder', 'heading')  # 保存的文件夹

        if not token:
            return APIResponse(data_msg="缺少参数token")

        if not image:
            return APIResponse(data_msg="图片未上传!")

        # 获取redis中的token
        redis_conn = django_redis.get_redis_connection('token')
        real_image_token = redis_conn.get('image_token_{}'.format(user_id))

        # token失效
        if real_image_token is None:
            return APIResponse()

        real_iamge_token = real_image_token.decode()
        if token != real_iamge_token:
            return APIResponse(data_msg="token错误!")

        image_md5 = PictureStorageToolClass().calculate_image_md5(image)
        image_obj = Image.objects.filter(img_md5=image_md5).first()

        # 如果上传的图片不重复
        if not image_obj:
            # 判断文件大小
            image_size = image.size
            image_name = image.name
            res_size = PictureStorageToolClass().file_size(image_size)
            if not res_size:
                return APIResponse(data_msg="文件大小不能超过5M!")

            # 判断文件类型
            image_type = PictureStorageToolClass().precise_type(image)

            # 如果是图片, 判断图片后缀
            if image_type.split('/')[0] == 'image':
                image_type = image_name.split('.')[-1]
                res_type = PictureStorageToolClass().judge_type(image_type)
                if not res_type:
                    return APIResponse(data_msg="图片后缀错误!")

            # 定义图片存储路径
            root_path = PictureStorageToolClass().storage_path(folder)

            # 保存文件
            uuid_iamge_name, img_path = PictureStorageToolClass().save_iamge(root_path, image_name, image)

            if not uuid_iamge_name:
                return APIResponse(data_msg="保存文件失败,请重试!")

            # 外部访问的路径(因为在总url中写了要以image开头)
            outside_url = '/image/' + folder + '/' + uuid_iamge_name

            # 表保存数据
            Image.objects.create(
                user_id=1,
                img_name=image_name,
                img_md5=image_md5,
                img_type=image_type,
                img_size=image_size,
                img_path=img_path,
                img_url=outside_url,
            )

            # 外面访问的完整路径(包括域名)
            entirely_outside_url = conf.TEST_DOMAIN_NAME + outside_url

            return APIResponse(data=entirely_outside_url, data_msg="上传成功")

        # 如果上传的图片重复,则直接返回路径
        else:
            image_url = conf.TEST_DOMAIN_NAME + image_obj.img_url
            return APIResponse(data=image_url, data_msg="上传成功")


def upload_imgs(request):
    '''
        model拆分成2个表，其中一个为文件存储，一个为图集
        图集对文件存储中需要有一个字段设置为多对多的储存关系
        post后获得文件
        先对图集实例化，增加其他字段应填写的值，对这个实例存储
        再对多文件列表循环，对图片本身实例化，增加其他字段应填写的值，再对这个实例存储
        最后添加图片对应图集的关系表保存
    :param request:
    :return:
    '''
    test = Entry2ExitDeclaration()
    test.name = 'test' + str(random.randint(100, 900))
    test.save()
    for f in request.FILES.getlist('imgs'):
        print(f)
        empt = SupportingImgs()
        # 增加其他字段应分别对应填写
        empt.single = f
        empt.img = f
        empt.save()
        test.imgs.add(empt)

        # File(file=f, files=test,id=1).save()
    return HttpResponse('上传成功')


class MessageEmail(APIView):
    def get(self, request, *args, **kwargs):
        """
        发送手机/邮箱验证码
        :return:data = {"status": status, "message": message}
        """
        data = {"status": False, "message": None}
        # 1.获取手机号（邮箱）

        email = request.query_params.get("email")

        # 2.手机格式校验，由于短信验证收费，开发测试采用邮箱验证
        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response(data)

        # 3.生成随机验证码
        random_code = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(
            random.randint(0, 9))
        print(random_code)
        # 发送邮箱验证码
        try:
            # message_status = send_mail(subject="验证码", message=f"欢迎您注册，您的验证码为：\n{random_code}\n有效时间为5分钟",
            #                            from_email=settings.EMAIL_HOST_USER, recipient_list=[email], )
            message_status = True
        except:
            message_status = False
        # 4.验证码发送到手机上,购买短信服务，阿里云/腾讯云短信
        # TODO tencent.sent_message(phone,random_code)

        """
        5.验证码+手机号+有效时间保留（30s过期）
            5.1 搭建redis服务(有云服务器，暂时采用本地redis服务器)
            5.2 django中方便使用redis模块django-redis
                配置：settings文件添加
                    CACHES = {
                        "default": {
                            "BACKEND": "django_redis.cache.RedisCache",
                            'LOCATION': 'redis://127.0.0.1:6379/1',
                            "OPTIONS": {
                                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                                "CONNECTION_POOL_KWARGS": {
                                    "max_connections": 100
                                },
                            },
                        }
                    }
            5.3 引入redis
                from django_redis import get_redis_connection
                conn = get_redis_connection()
                conn.set(email, random_code, ex=30)
        """

        #  邮箱发送，发送成功存入数据库
        if message_status:
            cache.set(email, random_code, 60 * 60 * 24)  # 设置5分钟有效
            data["status"] = True
            data["message"] = "验证码发送成功！"
        else:
            data["message"] = "验证码发送失败！"
        return Response(data)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        """
        登录验证
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = {"status": False, "data": {}}

        ser = LoginSerializer(data=request.data)
        # 验证邮箱与验证码的合法性,并校验
        if not ser.is_valid():
            return Response(data)

        email = ser.validated_data.get("email")
        code = ser.validated_data.get("code")
        redis_code = cache.get(email)
        if code != redis_code:
            return Response(data)

        """不存在则创建"""

        user_info, flag = UserInfo.objects.get_or_create(email=email, )
        user_info.token = str(uuid.uuid4)
        user_info.save()

        data["status"] = True
        data['data'] = {
            'token': user_info.token,
            'email': email
        }
        return Response(data)
