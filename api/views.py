# Create your views here.
# from rest_framework.response import JsonResponse
import datetime
import json
import logging
import random
import uuid

import django_redis
import requests
from django.conf import settings
# from django.core import serializers
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.forms import model_to_dict
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import *
from api.serializer.account import *
from api.utils import PictureStorageToolClass, copy_file
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
        print(redis_code)
        print(phone)
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

        data = {"status": False, }
        try:
            user = UserInfo.objects.get(openid=openid)
            # print("basics_info", user.basics_info.id)
            if user.basics_info:
                data["status"] = True
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
    完善个人信息,更新个人信息
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
        print(userInfo)

        if not ownership:
            ownership = None
        else:
            ownership = int(ownership)
        gender = int(userInfo.get("gender"))

        user_basics_info = UserInfo.objects.get(openid=openid)
        status = 0
        # if not user_obasics_info.basics_info:
        #     data["code"] = -1
        #     print("data", data)
        #     return Response(data)
        if is_admin == 1:
            status = 1

        try:

            user = BasicsUserInfo.objects.create(is_admin=is_admin, name=name, id_number=id_number, native=native,
                                                 address=address, phone=phone, email=email, gender=gender,
                                                 status=status, ownership_id=ownership)

            user_basics_info.basics_info = user
            user_basics_info.save()
        except:
            if not user_basics_info.basics_info:
                data["code"] = -1
                print("data", data)
                return Response(data)
            user = BasicsUserInfo.objects.get(id_number=id_number)
            # user.phone = phone
            user.email = email
            user.address = address
            user.save()
        finally:

            user = BasicsUserInfo.objects.get(id=user_basics_info.basics_info_id)
            car = userInfo.get("car")
            for _ in car:
                try:
                    Car.objects.create(user=user, carNo=_.get('carNo'), type=_.get('type'), color=_.get('color'))
                except:
                    try:
                        c = Car.objects.get(carNo=_.get('carNo'), user=user, )
                    except:
                        data['msg'] = "车牌%s已经被其他用户添加" % _.get('carNo')
                        return Response(data)
                    c.type = _.get("type")
                    c.color = _.get("color")
                    c.save()

        data["status"] = True
        data["user_status"] = user.status

        print("data", data)
        return Response(data)


class AuditList(APIView):
    """
    获取审核表(未审核)
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False, }
        print(request.GET)
        openid = request.GET.get("openid")
        # code = request.GET.get("code")

        page = request.GET.get("page")
        status = request.GET.get("status")
        try:
            if not page:
                page = 1
            else:
                page = int(page)
            size = request.GET.get("size")
            if not size:
                size = 10
            else:
                size = int(size)
            if not status:
                status = 3
            else:
                status = int(status)
        except:
            return Response(data)

        try:
            # AdminUserInfo.objects.get(user_info__userinfo__openid=openid, admin_post=5)
            admin_user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.pk)
            is_admin = admin_user.is_admin
            if is_admin not in (2, 4, 5):
                return Response(data)
        except:
            return Response(data)

        response_list = BasicsUserInfo.objects.all()

        if status != 3:
            response_list = response_list.filter(status=status)
        if response_list.exists():
            paginator = Paginator(response_list, size)
            count = paginator.count
            if page > count:
                page = 1
            contacts = paginator.page(page).object_list
            from django.core import serializers
            son_data = serializers.serialize("python", contacts, ensure_ascii=False)

            son_data = [i.get("fields") for i in son_data]
            data['data'] = son_data
            data['count'] = count

        else:
            data['data'] = []
            data['count'] = 0
        data['status'] = True

        print("data", data)
        return Response(data)


class GetCommunityList(APIView):
    """
    获取社区/哨卡列表
    """

    def get(self, request, *args, **kwargs):
        data = {"data": [], "count": 0, "category": -1}
        category = request.GET.get("category")
        print("category", category)
        try:
            data['category'] = int(category)
        except:
            return Response(data)

        community_list = Community2LigaturesInfo.objects.filter(category=data['category'])
        data['count'] = community_list.count()

        for i in community_list:
            data['data'].append({"id_number": i.id, "name": i.name})
        return Response(data)


class GetAuditLog(APIView):
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


# class Test(APIView):
#     def get(self, request, *args, **kwargs):
#         data = {"status": True, "data": "666"}
#         return Response(data)


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


class ForeignWorkersRegistration(APIView):
    """
    发起外来人员登记
    """

    def post(self, request, *args, **kwargs):
        prams = request.data
        data = {"status": False, }
        openid = prams.get("openid")
        name = prams.get("name")
        gender = prams.get("gender")
        phone = prams.get("phone")
        id_number = prams.get("id_number")
        visiting_reason = prams.get("visiting_reason")
        code = prams.get("code")

        health_code = prams.get("health_code")
        travel_card = prams.get("travel_card")
        cov_report = prams.get("cov_report")

        ser = ForeignWorkersSerializer(data=prams)
        # print("prams", prams)
        # print("health_code", health_code)
        # print("travel_card", travel_card)
        # print("cov_report", cov_report)

        if not ser.is_valid():
            # for i in ser.errors.items():
            #     print(i)
            # data['msg'] = '请输入正确的信息！'
            data['msg'] = ser.errors.items()
            return Response(data)

        user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info_id)
        if user.status != 1:
            data['msg'] = '您当前状态不可发起外来人员登记！'
            return Response(data)

        is_admin = user.is_admin
        status = 0
        upload_to = ForeignWorkers.UPLOAD_TO
        try:
            code = int(code)
            if code == 0:
                ForeignWorkers.objects.get(by_user=user, id_number=id_number, is_valid=True)
                data['msg'] = '请勿重复添加！'
                return Response(data)
            elif code == 1:
                try:
                    copy_file(health_code=health_code, travel_card=travel_card, cov_report=cov_report,
                              model=ForeignWorkers)
                except:
                    return Response(data)
                _ = ForeignWorkers.objects.exclude(status=1).get(by_user=user, id_number=id_number)

                _.name = name
                _.gender = gender
                _.phone = phone
                _.visiting_reason = visiting_reason

                _.health_code = upload_to + health_code
                _.travel_card = upload_to + travel_card
                _.cov_report = upload_to + cov_report
                _.save()

                data = {"status": True}
                return Response(data)
            else:
                return Response(data)
        except:
            if code == 0:
                # 权限待定
                if is_admin == 4 or is_admin == 5 or is_admin == 2:
                    status = 1
                try:
                    copy_file(health_code=health_code, travel_card=travel_card, cov_report=cov_report,
                              model=ForeignWorkers)
                except:
                    return Response(data)
                _ = ForeignWorkers(name=name, gender=gender, id_number=id_number, phone=phone, status=status,
                                   visiting_reason=visiting_reason, health_code=upload_to + health_code,
                                   travel_card=upload_to + travel_card, cov_report=upload_to + cov_report,
                                   by_user=user)
                _.save()

                data = {"status": True}
                return Response(data)

            elif code == 1:
                return Response(data)
            return Response(data)


class GetForeignWorkersRegistration(APIView):
    """
    查询外来人员登记记录
    """

    def get(self, request, *args, **kwargs):
        prams = request.GET
        data = {"status": False, }
        openid = prams.get("openid")
        status = prams.get("status")
        page = prams.get("page")
        size = prams.get("size")

        # print(prams)
        ser = GetForeignWorkersSerializer(data=prams)
        if not ser.is_valid():
            data['code'] = -1
            data['msg'] = ser.errors
            # print(data)
            return Response(data)

        user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
        is_admin = user.is_admin

        if user.status != 1:
            data['code'] = 0
            return Response(data)

        # 权限问题待定
        if is_admin == 4 or is_admin == 5 or is_admin == 2:
            result = ForeignWorkers.objects.filter()
        else:
            result = ForeignWorkers.objects.filter(by_user=user.id)
        status = int(status)
        if status != 3:
            result = result.filter(status=status)
        result = result.order_by("-create_time")
        if result.exists():
            paginator = Paginator(result, size)
            count = paginator.count
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:  # 不是数字
                posts = paginator.page(1)
            except EmptyPage:  # 超出页码范围
                posts = paginator.page(paginator.num_pages)
            contacts = posts.object_list
            from django.core import serializers

            son_data = serializers.serialize("python", contacts, ensure_ascii=False)
            res = []
            for i in son_data:
                i = i.get("fields")

                i['health_code'] = settings.MEDIA_URL + i['health_code']
                i['travel_card'] = settings.MEDIA_URL + i['travel_card']
                i['by_user'] = BasicsUserInfo.objects.get(pk=i['by_user'])

                i['cov_report'] = settings.MEDIA_URL + i['cov_report']
                i['create_time'] = datetime.datetime.strftime(i['create_time'], '%Y-%m-%d %H:%M:%S')
                if i['audit_time']:
                    i['audit_time'] = datetime.datetime.strftime(i['audit_time'], '%Y-%m-%d %H:%M:%S')
                # del i['id']
                del i['by_user']
                res.append(i)

            data['data'] = res
            data['count'] = count

        else:
            data['data'] = []
            data['count'] = 0
        data['status'] = True
        return Response(data)


class ReForeignWorkersRegistration(APIView):
    """
    管理员审核外来人员信息
    """

    def post(self, request, *args, **kwargs):
        prams = request.data
        data = {"status": False}
        openid = prams.get("openid")
        status = prams.get("status")
        id_number = prams.get("id_number")

        ser = ReForeignWorkersSerializer(data=prams)
        if not ser.is_valid():
            return Response(data)
        status = int(status)
        try:
            _ = ForeignWorkers.objects.get(id_number=id_number, is_valid=True)
        except:
            return Response(data)
        if _.status != 0:
            return Response(data)

        user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
        if user.status != 1:
            return Response(data)
        is_admin = user.is_admin

        if is_admin in (2, 4, 5):
            _.status = status
            _.audit_time = timezone.now()
            _.save()
            data['status'] = True
            return Response(data)

        return Response(data)


class EntryAndExitDeclaration(APIView):
    """
    社区居民提起出入申报
    """

    def post(self, request, *args, **kwargs):
        prams = request.data

        data = {"status": False}

        openid = prams.get("openid")
        subject_matte = prams.get("subject_matte")
        start_time = prams.get("start_time")
        end_time = prams.get("end_time")

        start_time = timezone.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
        end_time = timezone.datetime.strptime(end_time, '%Y-%m-%d %H:%M')

        health_code = prams.get("health_code")
        travel_card = prams.get("travel_card")
        cov_report = prams.get("cov_report")

        Supporting_imgs = prams.get("supportingMaterials")
        print("SupportingImgs", SupportingImgs, type(SupportingImgs))

        # return Response("ok")

        ser = EntryAndExitDeclarationSerializer(data=prams)
        if not ser.is_valid():
            for k, v in ser.errors.items():
                print(k, v)
            data['code'] = -1
            data['msg'] = ser.errors
            return Response(data)
        upload_to = Entry2ExitDeclaration.UPLOAD_TO
        try:
            user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
        except:
            return Response(data)
        _ = Entry2ExitDeclaration.objects.filter(is_valid=True).filter(user=user)

        if _:
            data['code'] = 0
            return Response(data)
        copy_file(health_code=health_code, travel_card=travel_card, cov_report=cov_report, model=Entry2ExitDeclaration)
        _ = Entry2ExitDeclaration(user=user, subject_matte=subject_matte, start_time=start_time, end_time=end_time,
                                  health_code=upload_to + health_code, travel_card=upload_to + travel_card,
                                  cov_report=upload_to + cov_report)
        _.save()

        for i in Supporting_imgs:
            copy_file(img=i, model=SupportingImgs)
            upload_to = SupportingImgs.UPLOAD_TO
            SupportingImgs.objects.create(img=upload_to + i, for_declaration=_)

        data['status'] = True
        return Response(data)


class GetEntryAndExitDeclaration(APIView):
    """
    查询申报记录
    """

    def get(self, request, *args, **kwargs):
        prams = request.GET

        data = {"status": False}
        openid = prams.get("openid")
        status = prams.get("status")
        page = prams.get("page")
        size = prams.get("size")
        ser = GetEntryAndExitDeclarationSerializer(data=prams)
        if not ser.is_valid():
            data['code'] = -1
            data['msg'] = ser.errors

            return Response(data)

        try:
            status = int(status)
            size = int(size)
            user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.pk)
            is_admin = user.is_admin

        except:
            return Response(data)
        if is_admin == 1:
            result = Entry2ExitDeclaration.objects.filter(user=user)

        elif is_admin in (2, 4, 5):
            result = Entry2ExitDeclaration.objects.filter()
        else:
            return Response(data)
        result = result.order_by("-create_time")
        if status != 3:
            result = result.filter(status=status)

        # 数据分页返回
        if result.exists():
            paginator = Paginator(result, size)
            count = paginator.count
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:  # 不是数字
                posts = paginator.page(1)
            except EmptyPage:  # 超出页码范围
                posts = paginator.page(paginator.num_pages)
            contacts = posts.object_list
            from django.core import serializers
            son_data = serializers.serialize("python", contacts, ensure_ascii=False)
            res = []
            for i in son_data:
                i = i.get("fields")
                del i['user']
                i['health_code'] = settings.MEDIA_URL + i['health_code']
                i['travel_card'] = settings.MEDIA_URL + i['travel_card']
                i['cov_report'] = settings.MEDIA_URL + i['cov_report']
                i['create_time'] = datetime.datetime.strftime(i['create_time'], '%Y-%m-%d %H:%M:%S')
                if i['audit_time']:
                    i['audit_time'] = datetime.datetime.strftime(i['audit_time'], '%Y-%m-%d %H:%M:%S')
                res.append(i)
            data['data'] = res
            data['count'] = count
            data['page'] = posts.number
            data['size'] = size
        else:
            data['data'] = []
            data['count'] = 0
        data['status'] = True
        return Response(data)


class ReEntryAndExitDeclaration(APIView):
    """
    网格员审批社区人员外出申报
    """

    def post(self, request, *args, **kwargs):
        prams = request.data

        data = {"status": False}

        ser = ReEntryAndExitDeclarationSerializer(data=prams)
        if not ser.is_valid():
            return Response(data)
        openid = prams.get("openid")
        status = int(prams.get("status"))
        id_number = prams.get("id_number")
        is_valid = True
        if status == -1:
            is_valid = False
        try:

            admin_user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
            is_admin = admin_user.is_admin

            if is_admin not in (2, 4, 5):
                return Response(data)

            user = BasicsUserInfo.objects.get(id_number=id_number)

            _ = Entry2ExitDeclaration.objects.get(status=0, is_valid=True, user=user)


        except:
            return Response(data)

        _.status = status
        _.is_valid = is_valid
        _.save()

        # 创建审核记录
        AuditLog.objects.create(status=status, auditor=admin_user, audited_user=user)

        data['status'] = True
        return Response(data)


class AddUser(APIView):
    """
    网格员新增人员
    """

    def post(self, request, *args, **kwargs):
        prams = request.data
        data = {"status": False}
        return Response(data)


class UploadImg(APIView):
    """
    上传图片至临时文件夹
    """

    def post(self, request, *args, **kwargs):

        myfile = request.FILES
        data = {"status": False}
        my_file = myfile.get("file")

        try:
            if my_file:
                suffix = my_file.name.split('.')[-1]

                now_time = datetime.datetime.now().strftime('%Y%m%d')
                end_random = "%05d" % random.randint(0, 10000)

                my_file.name = now_time + "%05d" % AutoImgName.objects.create().pk + end_random + "." + suffix

                _ = ImgUpload(img=my_file)
                _.save()
                url = _.img.url.split("/img/temp/")[1]

                data['status'] = True
                data['img_path'] = url
            print(data)
        except Exception as e:
            print(e)
        return Response(data)


class Test(APIView):
    """
    测试
    """

    def post(self, request, *args, **kwargs):
        prams = request.data
        myfile = request.FILES
        data = {"status": False, "msg": None}

        openid = prams.get("openid")
        name = prams.get("name")
        gender = prams.get("gender")
        phone = prams.get("phone")
        id_number = prams.get("id_number")
        visiting_reason = prams.get("visiting_reason")
        code = prams.get("code")

        health_code = myfile.get("health_code")
        travel_card = myfile.get("travel_card")
        cov_report = myfile.get("cov_report")
        print("prams", prams)
        print("myfile", myfile)
