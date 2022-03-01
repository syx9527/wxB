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
from django.core.cache import caches
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.middleware.csrf import get_token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.Tencent.sms import send_massages
from api.models import *
from api.serializer.account import *
from api.utils import PictureStorageToolClass, copy_file
from imageserver.utils import conf
from imageserver.utils.api_response import APIResponse

logger = logging.getLogger('django')


def check_code_cache(phone, code):
    redis_code = cache.get(phone)
    # cache.delete(phone, version=None)
    if not (phone or code):
        return False
    if code == redis_code:
        return True
    return False


def check_is_admin(openid):
    try:
        admin_user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info_id)

        is_admin = int(admin_user.is_admin)

        if is_admin not in (2, 3, 4, 5):
            return False
    except Exception as e:
        print(e)
        return False
    return True


def send_message(phone):
    data = {"status": False, }
    # 1.获取手机号（邮箱）

    # print(request.GET)

    # 2.手机格式校验，由于短信验证收费，开发测试采用邮箱验证
    ser = MessageSerializer(data={"phone": phone})
    if not ser.is_valid():
        return Response(data)
    code = cache.get(phone)
    if code:
        # send_massages(phone=phone, code=code)
        cache.delete("phone")
        data['status'] = True
        data["code"] = code
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
    except Exception as e:
        print(e)
        message_status = False

    #  验证码发送，发送成功存入数据库
    if message_status:
        print(random_code)
        cache.set(phone, random_code, settings.CACHES_TIME_OUT)  # 设置有效时长，单位  秒
        data["status"] = True
        # data["message"] = "验证码发送成功！"
        data["code"] = random_code
    # else:
    # data["message"] = "验证码发送失败！"
    # print(data, type(data))
    return data


# class GetToken(View):
class GetToken(APIView):
    """
    获取csrf_token
    """

    def get(self, request):
        token = get_token(request)
        # print(token)
        # return JsonResponse({"res": 0, "token": token})
        return Response({"res": 0, "token": token})


class GetUserInfo(APIView):
    """
    用户获取个人信息
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False}

        prams = request.GET
        openid = prams.get("openid")
        ser = CheckOpenid(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        try:
            res = BasicsUserInfo.objects.filter(pk=UserInfo.objects.get(openid=openid).basics_info_id).values().first()

            res['born'] = datetime.datetime.strftime(res['born'], '%Y-%m-%d')
            res['ownership'] = Community2LigaturesInfo.objects.get(pk=res['ownership_id']).name
            cars = Car.objects.filter(user_id=res['id'])
            car = []
            if cars:
                for i in cars:
                    car.append({"carNo": i.carNo})
            res['car'] = car
            gender = {
                1: "男",
                0: "女",
            }

            res['gender'] = gender.get(res['gender'])
            res['avatar_url'] = settings.MEDIA_URL + res['avatar_url']
            del res['ownership_id']
            del res['id']
            data['data'] = res
            data['status'] = True
        except Exception as e:
            print(e)
            return Response(data)
        return Response(data)


class GetTrafficRecord(APIView):
    """
    用户个人通行记录
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False}

        prams = request.GET

        ser = CheckOpenid(data=prams)

        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = prams.get("openid")
        size = prams.get("size")
        page = prams.get("page")

        try:
            user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info_id)

            result = TrafficRecord.objects.filter(person=user).order_by("-create_time")

            if result.exists():
                try:
                    paginator = Paginator(result, size)

                except ValueError:
                    paginator = Paginator(result, 10)
                    size = 10
                # paginator = Paginator(result, size)
                count = paginator.count
                try:
                    posts = paginator.page(page)
                except PageNotAnInteger:  # 不是数字
                    posts = paginator.page(1)
                    page = 1
                except EmptyPage:  # 超出页码范围
                    posts = paginator.page(paginator.num_pages)
                    page = paginator.num_pages
                has_next = posts.has_next()
                page = int(page)
                size = int(size)
                contacts = posts.object_list
                from django.core import serializers

                son_data = serializers.serialize("python", contacts, ensure_ascii=False)
                res = []
                ENTER_OR_OUT = {
                    2: "外出社区",
                    1: "进入社区",
                }
                STATUS = {
                    1: "审核通过",
                    -1: "审核未通过",
                }

                for i in son_data:
                    i = i.get("fields")
                    i['ex_status'] = ENTER_OR_OUT.get(i['ex_status'])
                    i['status'] = STATUS.get(i['status'])
                    i['create_time'] = datetime.datetime.strftime(i['create_time'], '%Y-%m-%d %H:%M:%S')
                    i['address'] = Community2LigaturesInfo.objects.get(pk=i['address']).name

                    del i['admin']
                    del i['person']
                    del i['for_ex']
                    res.append(i)
                data['data'] = res
                data['count'] = count
                data['size'] = size
                data['page'] = page
                data['has_next'] = has_next

            else:
                data['data'] = []
                data['count'] = 0
            data['status'] = True
        except Exception as e:
            print(e, )

        return Response(data)


def create_new_user(openid):
    cache_user_info = caches['user_info'].get(openid)

    if not cache_user_info:
        return False
    print("cache_user_info", cache_user_info)
    # openid = cache_user_info.get("openid")
    name = cache_user_info.get("name")
    id_number = cache_user_info.get("id_number").upper()
    native = cache_user_info.get("native")
    address = cache_user_info.get("address")
    phone = cache_user_info.get("phone")
    email = cache_user_info.get("email")
    gender = cache_user_info.get("gender")
    ownership = cache_user_info.get("ownership")
    car = cache_user_info.get("car")
    avatar_url = cache_user_info.get("avatar_url")

    try:

        ba_avatar_url = caches['new_wx'].get(openid, )
        upload_to = BasicsUserInfo.UPLOAD_TO
        user = BasicsUserInfo.objects.create(name=name, id_number=id_number, native=native,
                                             address=address, phone=phone, email=email, gender=gender,
                                             ownership_id=ownership, avatar_url=upload_to + avatar_url)

        copy_file(model=BasicsUserInfo, avatar_url=avatar_url, )

        UserInfo.objects.create(openid=openid, avatar_url=ba_avatar_url, basics_info_id=user.id)

        if car:
            for _ in car:
                try:
                    Car.objects.get(user=user, carNo=_.get('carNo'))
                    # message_status = True
                except Exception as e:
                    print(e)
                    try:
                        c = Car.objects.create(carNo=_.get('carNo'), user=user, )
                        c.save()
                    except Exception as e:
                        print(e)

        return True
    except Exception as e:
        print(e)

        return False


class NewUserCheckOldUser(APIView):
    """
    新用户绑定老用户信息校验
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        ser = NewUserCheckOldUserrDeclarationSerializer(data=request.data)
        if not ser.is_valid():
            return Response(data)
        name = ser.validated_data.get("name")
        phone = ser.validated_data.get("phone")
        openid = ser.validated_data.get("openid")
        id_number = ser.validated_data.get("id_number").upper()
        _ = BasicsUserInfo.objects.filter(name=name, phone=phone, id_number=id_number)
        print(ser.validated_data)
        if _:
            data['status'] = True
            basics_info = _.first().pk
            caches['new_to_old'].set(openid, basics_info)
        print("new_to_old", data)
        return Response(data)


class CheckCode(APIView):
    """
    校验验证码
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        phone = request.data.get("phone")
        code = request.data.get("code")
        op = request.data.get("op")
        print(request.data)
        # op = {
        #     "opcode": 0,
        #     "openid": "syx"
        # }

        # op = json.loads(op)

        print(phone, code)

        if not (phone and code):
            print(1)
            return Response(data)
        status = check_code_cache(phone, code)
        if not status:
            print(2)
            return Response(data)
        if not op:
            cache.delete(phone)
            data["status"] = status
            print(3)
            return Response(data)
        try:

            opcode = op.get("opcode")

            openid = op.get("openid")
            print(opcode, openid)
            if not op:
                print(4)
                return Response(data)
            opcode = int(opcode)
            if opcode == 0:
                status = create_new_user(openid)
                data["status"] = status
                res = BasicsUserInfo.objects.filter(
                    pk=UserInfo.objects.get(openid=openid).basics_info_id).values().first()
                print(5)
                print(res)
                data['data'] = res
                return Response(data)
            elif opcode == 1:
                try:
                    print("Test OK !")
                    basics_info = caches['new_to_old'].get(openid)
                    avatar_url = caches['new_wx'].get(openid)
                    UserInfo.objects.create(openid=openid, avatar_url=avatar_url, basics_info_id=basics_info)
                    _ = BasicsUserInfo.objects.filter(pk=basics_info).values().first()
                    try:
                        cache.delete(phone)
                    except Exception as e:
                        pass
                    data["status"] = True
                    data["data"] = _
                    print("*****" * 8, "\n", data)
                    return Response(data)
                except Exception as e:
                    print(e)
                    print(6)
                    return Response(data)
            else:
                print(7)
                return Response(data)

        except Exception as e:
            print(e)
            print(8)
            return Response(data)


class Message(APIView):
    def get(self, request, *args, **kwargs):
        """
        发送手机
        :return:data = {"status": status, "message": message}
        """

        phone = request.GET.get("phone")

        data = {"status": False, }
        # 1.获取手机号（邮箱）

        # print(request.GET)

        # 2.手机格式校验，由于短信验证收费，开发测试采用邮箱验证
        ser = MessageSerializer(data=request.GET)
        if not ser.is_valid():
            return Response(data)
        if cache.get(phone):
            print(phone, cache.get(phone))
            data["status"] = True
            data["code"] = cache.get(phone)
            data["message"] = "验证码5分钟有效！"
            return Response(data)

        # 3.生成随机验证码
        random_code = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(
            random.randint(0, 9))

        # 4.验证码发送到手机上,购买短信服务，阿里云/腾讯云短信
        # TODO tencent.sent_message(phone,random_code)
        # 发送邮箱验证码
        # try:
        #     # message_status = send_mail(subject="验证码", message=f"欢迎您注册，您的验证码为：\n{random_code}\n有效时间为5分钟",
        #     #                            from_email=settings.EMAIL_HOST_USER, recipient_list=[email], )
        #     message_status = True
        #         except Exception as e:
        #             print(e)
        #     message_status = False
        #
        #  验证码发送，发送成功存入数据库
        message_status = send_massages(phone=phone, code=random_code)
        # message_status = True
        if message_status:
            print(random_code)
            cache.set(phone, random_code, settings.CACHES_TIME_OUT)  # 设置有效时长，单位  秒
            data["status"] = True
            data["message"] = "验证码发送成功！"
            data["code"] = random_code
        else:
            data["message"] = "验证码发送失败！"
        # data = send_message(phone)
        print(data)
        return Response(data)


class ReLogin(APIView):
    """
    重新登录
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False, }
        openid = request.data.get("openid")
        if not openid:
            return Response(data)

        try:

            pk = UserInfo.objects.get(openid=openid).basics_info_id

            user = BasicsUserInfo.objects.filter(pk=pk).values().first()
            res = {}
            res['status'] = user.get("status")
            res['is_admin'] = user.get("is_admin")
            res["openid"] = openid
            data["status"] = True
            data["data"] = res
            return Response(data)
        except Exception as e:
            print(e)
            # data["status"] = True

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
        print(code)
        print(code == redis_code)
        if code == redis_code:
            data["status"] = True

            try:
                res = BasicsUserInfo.objects.filter(phone=phone).values().first()
                openid = UserInfo.objects.get(basics_info=res.get("id")).openid
                # res = model_to_dict(user)
                if res['id']:
                    del res['id']
                res["openid"] = openid
                data["data"] = res
                # data["data"] = []
                return Response(data)


            except Exception as e:
                print(e)
                return Response(data)

        return Response(data)


class CheckBaseUser(APIView):
    """
    新微信绑定老用户
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False, }
        prams = request.data
        ser = MessageSerializer(data=prams)
        if not ser.is_valid():
            return Response(data)
        name = prams.get("name")
        openid = prams.get("openid")
        id_number = prams.get("id_number").upper()
        phone = prams.get("phone")

        try:
            BasicsUserInfo.objects.get(name=name, id_number=id_number, phone=phone)
            caches['base_user'].set(openid, id_number, settings.CACHES_TIME_OUT)
            data['status'] = True
            return Response(data)


        except Exception as e:
            print(e)
            return Response(data)
        pass

    def get(self, request, *args, **kwargs):
        data = {"status": False, }
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
        print(js_code)

        grant_type = settings.GRANT_TYPE

        # appId = "wxafe035d3c21ea4ef"
        # secret = "2b8b42cdce57e83bfdcfb3b21fe9b857"

        appId = settings.APPID
        secret = settings.SECRET

        # url_ = f"https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={secret}&js_code={js_code}&grant_type=authorization_code"
        # response_ = requests.get(url=url_)
        # response_ = json.loads(response_.text)
        # # url="https://api.weixin.qq.com/sns/oauth2/refresh_token?appid=APPID&grant_type=refresh_token&refresh_token=REFRESH_TOKEN"
        # print("response_", response_)
        # return Response("ok")

        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={secret}&js_code={js_code}&grant_type={grant_type}"

        response = requests.get(url=url)
        response = json.loads(response.text)
        # print("response", response)
        openid = response.get("openid")

        # 返回用户绑定的电话号码
        try:
            user = UserInfo.objects.get(openid=openid)
            phone = user.basics_info.phone
            data['phone'] = phone
        except Exception as e:
            print(e)
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

        avatar_url = userInfo.get("avatar_url")
        openid = userInfo.get("openid")

        data = {"status": False, }
        try:
            user = UserInfo.objects.get(openid=openid)
            # print("basics_info", user.basics_info.id)
            if user.basics_info:
                data["status"] = True
                user = BasicsUserInfo.objects.filter(id=user.basics_info.id).values().first()
                # res = model_to_dict(user)
                print("user", user)
                res = {
                    "status": user.get("status"),
                    "is_admin": user.get("is_admin"),
                    "avatar_url": user.get("avatar_url"),

                }
                data["data"] = res
        except Exception as e:
            print(e)

            # 创建缓存
            caches['new_wx'].set(openid, avatar_url, settings.CACHES_TIME_OUT)

            # user = UserInfo.objects.create(openid=openid)
            # user.nickName = nickName
            # user.gender = gender
            # user.language = language
            # user.city = city
            # user.province = province
            # user.country = country
            # user.avatar_url = avatar_url
            # user.save()

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
        print("userInfo", userInfo)
        ser = UserInfoSerializer(data=userInfo)

        # 验证身份证，电话号码，性别，邮箱，用户类别的合法性,并校验

        if not ser.is_valid():
            # data["msg"] = {}
            # print(ser.errors)
            data['msg'] = {}
            for k, v in ser.errors.items():
                data['msg'][k] = v[0]
                print(k, v[0])
            data["code"] = 0
            print("data", data)
            return Response(data)
        id_number = ser.validated_data.get("id_number").upper()
        openid = ser.validated_data.get("openid")
        # is_admin = int(userInfo.get("is_admin"))
        name = ser.validated_data.get("name")

        id_number = id_number.upper()  # 身份证最后若为X,将用户x转换为大写X
        native = ser.validated_data.get("native")

        _3 = Native.objects.get(value=native)
        _2 = Native.objects.get(pk=_3.father.id)
        _1 = Native.objects.get(pk=_2.father.id)
        native = "%s%s%s" % (_1, _2, _3)

        address = ser.validated_data.get("address")
        phone = ser.validated_data.get("phone")
        email = ser.validated_data.get("email")
        avatar_url = ser.validated_data.get("avatar_url")
        if not email:
            email = None
        ownership = userInfo.get("ownership")
        print(ser.validated_data)

        if not ownership:
            ownership = None
        else:
            ownership = int(ownership)
        gender = int(userInfo.get("gender"))

        # status = 0
        # if not user_obasics_info.basics_info:
        #     data["code"] = -1
        #     print("data", data)
        #     return Response(data)
        upload_to = BasicsUserInfo.UPLOAD_TO
        car = userInfo.get("car")
        try:
            user = UserInfo.objects.get(openid=openid)
            basics_user = BasicsUserInfo.objects.get(pk=user.basics_info_id)

            basics_user.name = name
            basics_user.id_number = id_number.upper()
            basics_user.native = native
            basics_user.address = address
            basics_user.avatar_url = upload_to + avatar_url
            basics_user.phone = phone
            basics_user.email = email
            basics_user.gender = gender
            # basics_user.status = status
            basics_user.ownership_id = ownership
            basics_user.save()
            try:
                copy_file(avatar_url=avatar_url, model=BasicsUserInfo)
            except Exception as e:
                print(e)
                return Response(data)

            for _ in car:
                try:
                    Car.objects.get(user=basics_user, carNo=_.get('carNo'))
                    break
                except Exception as e:
                    print(e)
                    try:
                        c = Car.objects.create(carNo=_.get('carNo'), user=basics_user, )
                        c.save()
                    except Exception as e:
                        print(e)
                        break

            user_status = 0
            if int(basics_user.status) != 1:
                user_status = 1
            data["status"] = True
            data["user_status"] = user_status
            print("data", data)
            return Response(data)
        except Exception as e:
            print(e)
            user_info_cache = {

                "name": name,
                "id_number": id_number.upper(),
                "native": native,
                "address": address,
                "phone": phone,
                "email": email,
                "gender": gender,
                "avatar_url": avatar_url,
                "ownership": ownership,
                "car": car
            }
            caches['user_info'].set(openid, user_info_cache, settings.CACHES_TIME_OUT)
            data["status"] = True
            # if not user_basics_info.basics_info:
            #     data["code"] = -1
            #     print("data", data)
            #     return Response(data)
            # user = BasicsUserInfo.objects.get(id_number=id_number)
            # # user.phone = phone
            # user.email = email
            # user.address = address
            # user.save()

        print("data", data)
        return Response(data)


class AuditList(APIView):
    """
    获取审核表(未审核)
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False, }
        # print(request.GET)
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
        except Exception as e:
            print(e)
            return Response(data)

        try:
            # AdminUserInfo.objects.get(user_info__userinfo__openid=openid, is_adamin=5)
            admin_user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.pk)
            is_admin = admin_user.is_admin
            if is_admin not in (2, 4, 5):
                return Response(data)
        except Exception as e:
            print(e)
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

        # print("data", data)
        return Response(data)


class AuditBasicsUserInfo(APIView):
    """
    获取审核表(未审核)
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False, }
        prams = request.data
        # print(prams)
        ser = AuditBasicsUserInfoSerializer(data=prams)
        if not ser.is_valid():
            # print(ser.errors.items())
            return Response(data)
        openid = ser.validated_data.get("openid")
        id_number = ser.validated_data.get("id_number").upper()
        op = int(ser.validated_data.get("op"))
        if not check_is_admin(openid):
            # print("not admin!")
            return Response(data)
        try:
            _ = BasicsUserInfo.objects.get(id_number=id_number)
            # print(_.status, _.name)
            if not _.status == 0:
                # print("已经审核")
                return Response(data)
            _.status = op
            _.save()
            # print("成功")
            data["status"] = True
            return Response(data)
        except Exception as e:
            print(e)
            print("用户不存在")
            return Response(data)

        # return Response(data)


class GetCommunityList(APIView):
    """
    获取社区/哨卡列表
    """

    def get(self, request, *args, **kwargs):
        data = {"data": [], "count": 0, "category": -1}
        prams = request.GET

        ser = GetCommunityListSerializer(data=prams)

        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        category = ser.validated_data.get("category")

        if category:

            community_list = Community2LigaturesInfo.objects.filter(category=int(category))
        else:
            community_list = Community2LigaturesInfo.objects.all()
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
        except Exception as e:
            print(e)
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
            cache.set(email, random_code, settings.CACHES_TIME_OUT)  # 设置5分钟有效
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

        ser = ForeignWorkersSerializer(data=prams)
        # print("prams", prams)
        # print("health_code", health_code)
        # print("travel_card", travel_card)
        # print("cov_report", cov_report)

        if not ser.is_valid():
            print(ser.errors)
            # for i in ser.errors.items():
            #     print(i)
            # data['msg'] = '请输入正确的信息！'
            data['msg'] = ser.errors.items()
            return Response(data)
        openid = prams.get("openid")
        name = prams.get("name")
        gender = prams.get("gender")
        phone = prams.get("phone")
        id_number = prams.get("id_number").upper()
        visiting_reason = prams.get("visiting_reason")
        code = prams.get("code")

        health_code = prams.get("health_code")
        travel_card = prams.get("travel_card")
        cov_report = prams.get("cov_report")
        avatar_url = ser.validated_data.get("avatar_url")
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
                ForeignWorkers.objects.get(by_user=user, id_number=id_number.upper(), is_valid=True)
                data['msg'] = '请勿重复添加！'
                return Response(data)
            elif code == 1:
                try:
                    copy_file(health_code=health_code, travel_card=travel_card, cov_report=cov_report,
                              avatar_url=avatar_url, model=ForeignWorkers)
                except Exception as e:
                    print(e)
                    return Response(data)
                _ = ForeignWorkers.objects.exclude(status=1).get(by_user=user, id_number=id_number.upper())

                _.name = name
                _.gender = gender
                _.phone = phone
                _.visiting_reason = visiting_reason

                _.health_code = upload_to + health_code
                _.travel_card = upload_to + travel_card
                _.cov_report = upload_to + cov_report
                _.avatar_url = upload_to + avatar_url
                _.save()

                data = {"status": True}
                return Response(data)
            else:
                return Response(data)
        except Exception as e:
            print(e)
            if code == 0:
                # 权限待定
                if is_admin == 4 or is_admin == 5 or is_admin == 2:
                    status = 1
                try:
                    copy_file(health_code=health_code, travel_card=travel_card, cov_report=cov_report,
                              avatar_url=avatar_url, model=ForeignWorkers)
                except Exception as e:
                    print(e)
                    return Response(data)
                _ = ForeignWorkers(name=name, gender=gender, id_number=id_number.upper(), phone=phone, status=status,
                                   visiting_reason=visiting_reason, health_code=upload_to + health_code,
                                   travel_card=upload_to + travel_card, cov_report=upload_to + cov_report,
                                   avatar_url=upload_to + avatar_url,
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

        query = prams.get("query")

        # print(prams)
        ser = GetForeignWorkersSerializer(data=prams)
        if not ser.is_valid():
            data['code'] = -1
            data['msg'] = ser.errors
            # print(data)
            print(ser.errors)
            return Response(data)

        openid = ser.validated_data.get("openid")
        status = ser.validated_data.get("status")
        page = ser.validated_data.get("page")
        size = ser.validated_data.get("size")
        if not size:
            size = 10
        user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
        is_admin = int(user.is_admin)

        if user.status != 1:
            data['code'] = 0
            return Response(data)

        # 权限问题待定
        if is_admin in (2, 3, 4, 5):

            result = ForeignWorkers.objects.filter()
            if is_admin == 3:
                result = result.filter(is_valid=True, status=1)
            if query:
                result = result.filter(Q(id_number__contains=query) | Q(name__contains=query) | Q(
                    phone__contains=query))

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
                page = 1
            except EmptyPage:  # 超出页码范围
                posts = paginator.page(paginator.num_pages)
                page = paginator.num_pages
            contacts = posts.object_list
            from django.core import serializers

            son_data = serializers.serialize("python", contacts, ensure_ascii=False)
            res = []
            for i in son_data:
                i = i.get("fields")

                i['health_code'] = settings.MEDIA_URL + i['health_code']
                i['avatar_url'] = settings.MEDIA_URL + i['avatar_url']
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
            data['size'] = size
            data['page'] = page

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
        id_number = prams.get("id_number").upper()

        ser = ReForeignWorkersSerializer(data=prams)
        if not ser.is_valid():
            return Response(data)
        status = int(status)
        try:
            _ = ForeignWorkers.objects.get(id_number=id_number, is_valid=True)
        except Exception as e:
            print(e)
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
        if is_admin in (2, 4, 5):
            _.status = status
            _.audit_time = timezone.now()
            _.save()
            data['status'] = True
            return Response(data)
        if is_admin == 3:
            if _.enter_status == 0:
                pass
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
        print(prams)

        Supporting_imgs = prams.get("supportingMaterials")
        # print("SupportingImgs", SupportingImgs, type(SupportingImgs))

        # return Response("ok")

        ser = EntryAndExitDeclarationSerializer(data=prams)
        if not ser.is_valid():
            for k, v in ser.errors.items():
                print(k, v)
            data['code'] = -1
            data['msg'] = ser.errors
            return Response(data)

        openid = ser.validated_data.get("openid")
        subject_matte = ser.validated_data.get("subject_matte")
        start_time = ser.validated_data.get("start_time")
        end_time = ser.validated_data.get("end_time")

        start_time = timezone.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
        end_time = timezone.datetime.strptime(end_time, '%Y-%m-%d %H:%M')

        health_code = ser.validated_data.get("health_code")
        travel_card = ser.validated_data.get("travel_card")
        cov_report = ser.validated_data.get("cov_report")
        upload_to = Entry2ExitDeclaration.UPLOAD_TO
        try:
            user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
        except Exception as e:
            print(e)
            return Response(data)
        _ = Entry2ExitDeclaration.objects.filter(is_valid=True).filter(user=user)

        if _:
            data['code'] = 0
            return Response(data)
        try:
            copy_file(health_code=health_code, travel_card=travel_card, cov_report=cov_report,
                      model=Entry2ExitDeclaration)
        except Exception as e:
            print(e)
            return Response(data)
        _ = Entry2ExitDeclaration(user=user, subject_matte=subject_matte, start_time=start_time, end_time=end_time,
                                  health_code=upload_to + health_code, travel_card=upload_to + travel_card,
                                  cov_report=upload_to + cov_report)
        _.save()

        try:
            for i in Supporting_imgs:
                copy_file(img=i, model=SupportingImgs)
                upload_to = SupportingImgs.UPLOAD_TO
                SupportingImgs.objects.create(img=upload_to + i, for_declaration=_)
        except Exception as e:
            print(e)
            return Response(data)

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


        except Exception as e:
            print(e)
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
                user = BasicsUserInfo.objects.get(pk=i['user'])

                i['id_number'] = user.id_number.upper()
                i['name'] = user.name
                del i['user']
                i['health_code'] = settings.MEDIA_URL + i['health_code']
                i['avatar_url'] = settings.MEDIA_URL + user.avatar_url.path
                i['travel_card'] = settings.MEDIA_URL + i['travel_card']
                i['cov_report'] = settings.MEDIA_URL + i['cov_report']
                i['create_time'] = datetime.datetime.strftime(i['create_time'], '%Y-%m-%d %H:%M:%S')
                i['start_time'] = datetime.datetime.strftime(i['start_time'], '%Y-%m-%d %H:%M:%S')
                i['end_time'] = datetime.datetime.strftime(i['end_time'], '%Y-%m-%d %H:%M:%S')
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
        id_number = prams.get("id_number").upper()

        try:

            admin_user = BasicsUserInfo.objects.get(pk=UserInfo.objects.get(openid=openid).basics_info.id)
            is_admin = admin_user.is_admin

            if is_admin not in (2, 4, 5):
                return Response(data)

            user = BasicsUserInfo.objects.get(id_number=id_number)

            _ = Entry2ExitDeclaration.objects.get(status=0, is_valid=True, user=user)



        except Exception as e:
            print(e)
            return Response(data)

        _.status = status
        _.auditor = admin_user
        _.save()

        # 创建审核记录
        # AuditLog.objects.create(status=status, auditor=admin_user, audited_user=user)

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


class DelUser(APIView):
    """
    网格员删除人员
    """

    def post(self, request, *args, **kwargs):
        prams = request.data
        print(prams)
        data = {"status": False}
        ser = DelUserSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = prams.get("openid")
        id_number = prams.get("id_number").upper()
        if not check_is_admin(openid):
            print("check")
            return Response(data)
        try:
            user = BasicsUserInfo.objects.get(id_number=id_number)
            print("Test OK! ---")
            user.delete()
            print("Test OK! ***")
            data['status'] = True
        except Exception as e:
            print(e)
            return Response(data)
        return Response(data)


class ReditUser(APIView):
    """
    网格员编辑人员
    """

    def post(self, request, *args, **kwargs):
        prams = request.data
        data = {"status": False, }

        ser = ReditUserInfoSerializer(data=prams)

        id_number = prams.get("id_number").upper()
        # 验证身份证，性别等信息的合法性,并校验
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
        openid = prams.get("openid")
        if not check_is_admin(openid):
            return Response(data)
        # is_admin = int(userInfo.get("is_admin"))
        name = prams.get("name")

        id_number = id_number.upper()  # 身份证最后若为X,将用户x转换为大写X
        native = prams.get("native")
        address = prams.get("address")
        # phone = prams.get("phone")
        gender = prams.get("gender")
        email = prams.get("email")
        ownership = prams.get("ownership")

        basics_user = BasicsUserInfo.objects.get(id_number=id_number)

        basics_user.name = name
        # basics_user.id_number = id_number
        basics_user.native = native
        basics_user.address = address
        # basics_user.phone = phone
        basics_user.email = email
        basics_user.gender = gender
        # basics_user.status = status
        basics_user.ownership_id = ownership
        basics_user.save()
        car = prams.get("car")
        for _ in car:
            try:
                Car.objects.get(user=basics_user, carNo=_.get('carNo'))
                break
            except Exception as e:
                print(e)
                try:
                    c = Car.objects.create(carNo=_.get('carNo'), user=basics_user, )
                    c.save()
                except Exception as e:
                    print(e)
                    break

        print(prams)
        return Response(data)


class FindUser(APIView):
    """
    网格员查找人员
    """

    def get(self, request, *args, **kwargs):
        prams = request.GET
        data = {"status": False}
        ser = FindUserSerializer(data=prams)
        if not ser.is_valid():
            return Response(data)

        openid = prams.get('openid')
        if not check_is_admin(openid):
            return Response(data)

        # book_obj = Book.objects.all().filter(Q(title__contains=query) | Q(publisher__name__contains=query))
        query = prams.get('query').upper()
        size = prams.get('size')
        page = prams.get('page')
        try:
            if size:
                size = int(size)
            else:
                size = 10
        except Exception as e:
            print(e)
            size = 10

        result = BasicsUserInfo.objects.filter(Q(id_number__contains=query) | Q(name__contains=query) | Q(
            phone__contains=query))
        result = result.exclude(is_admin=5)
        result = result.order_by("name")
        if result.exists():
            paginator = Paginator(result, size)
            count = paginator.count

            try:
                posts = paginator.page(page)
            except PageNotAnInteger:  # 不是数字
                posts = paginator.page(1)
            except EmptyPage:  # 超出页码范围
                posts = paginator.page(paginator.num_pages)
            page = posts.number
            contacts = posts.object_list
            from django.core import serializers

            son_data = serializers.serialize("python", contacts, ensure_ascii=False)
            res = []
            for i in son_data:
                pk = i.get("pk")
                car = []
                cars = Car.objects.filter(user_id=pk)
                if cars:
                    for c in cars:
                        car.append({"carNo": c.carNo})
                i = i.get("fields")
                i['car'] = car
                i['avatar_url'] = settings.MEDIA_URL + i['avatar_url']
                i['born'] = datetime.datetime.strftime(i['born'], '%Y-%m-%d')
                i['create_time'] = datetime.datetime.strftime(i['create_time'], '%Y-%m-%d %H:%M:%S')
                if i['ownership']:
                    _ = Community2LigaturesInfo.objects.get(pk=i['ownership'])
                    i['ownership'] = "%s-%s-%s" % (_.uid, _.name, _.address)
                else:
                    i['ownership'] = None
                res.append(i)

            data['data'] = res
            data['count'] = count
            data['page'] = page
            data['size'] = size
        else:
            data['data'] = []
            data['count'] = 0
            data['page'] = 1
            data['size'] = size
        data['status'] = True
        return Response(data)


class SentryPostFindUserByIdNumber(APIView):
    """
    哨卡员查询人员
    """

    def get(self, request, *args, **kwargs):
        sentry_post_find_user = 1
        data = {"status": False}
        prams = request.GET

        ser = FindUserByIdNumberSerializer(data=prams)
        if not ser.is_valid():
            return Response(data)

        openid = ser.validated_data.get("openid")
        user = BasicsUserInfo.objects.filter(pk=UserInfo.objects.get(openid=openid).basics_info.id)
        if user:
            user = user.first()
            if user.status != 1 or user.is_admin != 3:
                return Response(data)
        else:
            return Response(data)
        id_number = ser.validated_data.get("id_number").upper()
        try:

            user = BasicsUserInfo.objects.get(id_number=id_number)
            _ = Entry2ExitDeclaration.objects.filter(Q(user=user) & Q(is_valid=True))

            if _:

                res = _.values().first()

                res['name'] = user.name
                res['id_number'] = user.id_number
                res['gender'] = user.gender
                res['reason'] = res['subject_matte']
                del res['id']
                del res['user_id']
                del res['is_valid']
                del res['status']
                del res['subject_matte']
                del res['start_time']
                del res['end_time']
                del res['enter_status']
                data['status'] = True
                data['data'] = res
                return Response(data)
            else:
                return Response(data)

        except Exception as e:
            print(e)
            _ = ForeignWorkers.objects.filter(Q(id_number=id_number) & Q(is_valid=True))
            if _:
                res = _.values().first()
                del res['id']
                del res['status']
                del res['is_valid']
                del res['by_user_id']
                del res['enter_status']
                del res['create_time']
                res['user_type'] = 2
                res['health_code'] = settings.MEDIA_URL + res['health_code']
                res['travel_card'] = settings.MEDIA_URL + res['travel_card']
                res['cov_report'] = settings.MEDIA_URL + res['cov_report']
                res['avatar_url'] = settings.MEDIA_URL + res['avatar_url']

                # res['avatar_url'] = "/img/foreign_workers/202201110006600741.jpg"
                # res['address'] = "这是家庭地址"
                res['born'] = "1998-12-10"

                res['log'] = []
                logs = ForeignWorkersLog.objects.filter(foreign_worker=_.first())
                if logs:
                    for log in logs:
                        res['log'].append({
                            "time": datetime.datetime.strftime(log.create_time, '%Y-%m-%d %H:%M:%S'),
                            "ex_status": log.ex_status,
                            "address": log.address.name,
                            "status": log.status,
                            "reason": log.audit_reason,
                        })

                data['status'] = True
                data['data'] = res
                return Response(data)
        return Response(data)


class SentryPostReUserByIdNumber(APIView):
    """
    哨卡员审核人员进出
    """

    def post(self, request, *args, **kwargs):
        sentry_post_find_user = 1
        data = {"status": False}
        prams = request.data

        ser = RedUserByIdNumberSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = ser.validated_data.get("openid")
        id_number = ser.validated_data.get("id_number")
        status = int(ser.validated_data.get("status"))
        user_type = int(ser.validated_data.get("user_type"))
        reason = ser.validated_data.get("reason")
        user = UserInfo.objects.filter(openid=openid).first()
        admin_user = None
        if user:
            admin_user = BasicsUserInfo.objects.filter(pk=user.basics_info.id)

        if admin_user:
            admin_user = admin_user.first()
            if admin_user.status != 1 or admin_user.is_admin != 3:
                return Response(data)
        else:
            return Response(data)
        address = AdminUserInfo.objects.get(user_info=admin_user).admin_ownership

        if user_type == 1:
            _ = Entry2ExitDeclaration.objects.filter(Q(user__id_number=id_number) & Q(is_valid=True))
            if _:
                _ = _.first()

                if status == 1:
                    _.enter_status -= 1
                    enter_status = _.enter_status
                    _.save()
                if status == -1:
                    enter_status = _.enter_status - 1
                TrafficRecord.objects.create(person=BasicsUserInfo.objects.get(pk=_.user_id), ex_status=enter_status,
                                             admin=admin_user, address=address,
                                             audit_reason=reason, status=status, for_ex=_)
                data['status'] = True
        elif user_type == 2:
            _ = ForeignWorkers.objects.filter(Q(id_number=id_number) & Q(is_valid=True))
            if _:
                _ = _.first()
                enter_status = _.enter_status
                if status == 1:
                    enter_status += 1
                    _.enter_status = enter_status
                    _.save()

                ForeignWorkersLog.objects.create(foreign_worker=_, ex_status=_.enter_status, address=address,
                                                 audit_reason=reason, status=status, )
                data['status'] = True
        return Response(data)


def check_is_superuser(openid):
    try:
        pk = UserInfo.objects.get(openid=openid, ).basics_info_id
        user = BasicsUserInfo.objects.get(pk=pk, status=1)
        if int(user.is_admin) == 5:
            # print(user.is_admin)
            return True
    except Exception as e:
        # print(e)
        return False


class AdminAddCommunity2Ligature(APIView):
    """
    超级管理员增加社区/哨卡
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.data
        ser = AddCommunity2LigatureSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = ser.validated_data.get("openid")
        if not check_is_superuser(openid):
            return Response(data)

        name = ser.validated_data.get("name")
        category = int(ser.validated_data.get("category"))

        address = ser.validated_data.get("address")
        control_strategy = int(ser.validated_data.get("control_strategy"))
        try:
            Community2LigaturesInfo.objects.create(name=name, category=category, address=address,
                                                   control_strategy=control_strategy)
            data['status'] = True
        except Exception as e:
            print(e)
            return Response(data)
        return Response(data)


class AdminDelCommunity2Ligature(APIView):
    """
    超级管理员删除社区/哨卡
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.data
        ser = DelCommunity2LigatureSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = ser.validated_data.get("openid")

        if not check_is_superuser(openid):
            return Response(data)
        uid = ser.validated_data.get("uid")
        try:
            _ = Community2LigaturesInfo.objects.get(uid=uid)
            _.delete()
            data['status'] = True
        except Exception as e:
            print(e)
            return Response(data)

        return Response(data)


class AdminReCommunity2Ligature(APIView):
    """
    超级管理员编辑社区/哨卡
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.data
        ser = ReAddCommunity2LigatureSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = ser.validated_data.get("openid")
        if not check_is_superuser(openid):
            return Response(data)

        name = ser.validated_data.get("name")
        uid = ser.validated_data.get("uid")
        # category = int(ser.validated_data.get("category"))

        address = ser.validated_data.get("address")
        control_strategy = int(ser.validated_data.get("control_strategy"))
        try:
            _ = Community2LigaturesInfo.objects.get(uid=uid)
            _.name = name
            _.address = address
            _.control_strategy = control_strategy
            _.save()
            data['status'] = True
            print(_.name)
        except Exception as e:
            print(e)
            return Response(data)
        return Response(data)


class AdminFindCommunity2Ligature(APIView):
    """
    超级管理员查找社区/哨卡
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.GET
        ser = FindCommunity2LigatureSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)
        openid = ser.validated_data.get("openid")
        query = ser.validated_data.get("query")
        category = ser.validated_data.get("category")
        # address = ser.validated_data.get("address")
        page = ser.validated_data.get("page")
        size = ser.validated_data.get("size")

        if not check_is_superuser(openid):
            print(888)
            return Response(data)
        # uid = ser.validated_data.get("uid")

        result = Community2LigaturesInfo.objects.filter(Q(name__contains=query) | Q(address__contains=query))
        if category:
            category = int(category)
            result = result.filter(Q(category=category))
        result = result.order_by("name")
        if result.exists():
            try:
                paginator = Paginator(result, size)

            except TypeError as e:
                paginator = Paginator(result, 10)
                size = 10

            try:
                posts = paginator.page(page)
            except PageNotAnInteger:  # 不是数字
                posts = paginator.page(1)
            except EmptyPage:  # 超出页码范围
                posts = paginator.page(paginator.num_pages)
            count = paginator.count
            page = posts.number
            has_next = posts.has_next()
            size = len(posts)
            contacts = posts.object_list
            from django.core import serializers

            son_data = serializers.serialize("python", contacts, ensure_ascii=False)
            res = []
            for i in son_data:
                # print(i)
                fields = i.get("fields")
                imgs = []
                IMGS = Community2LigaturesImgs.objects.filter(name__uid=fields.get("uid"))
                if IMGS:
                    for IMG in IMGS:
                        img = IMG.img.url
                        imgs.append(img)
                fields['img'] = imgs
                res.append(fields)
            data['data'] = res
            data['count'] = count
            data['size'] = size
            data['page'] = page
            data['has_next'] = has_next
        else:
            data['data'] = []
            data['count'] = 0
            data['has_next'] = False
        data['status'] = True
        return Response(data)


class AdminAddUser(APIView):
    """
    超级管理员增加管理人员
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.data
        ser = AdminAddUserSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)

        openid = ser.validated_data.get("openid")

        if not check_is_superuser(openid):
            return Response(data)

        ownership = ser.validated_data.get("ownership")
        id_number = ser.validated_data.get("id_number")
        try:
            _ = AdminUserInfo.objects.filter(id_number=id_number)
            if _:
                data['code'] = -1
                return Response(data)
            admin_ownership = Community2LigaturesInfo.objects.get(pk=ownership)
            user_info = BasicsUserInfo.objects.get(id_number=id_number)
            AdminUserInfo.objects.create(admin_ownership=admin_ownership, user_info=user_info)
            data['status'] = True
            return Response(data)
        except Exception as e:
            print(e)
            return Response(data)

        return Response(data)


class AdminDelUser(APIView):
    """
    超级管理员删除管理人员
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.data
        ser = AdminDelUserSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)

        openid = ser.validated_data.get("openid")

        if not check_is_superuser(openid):
            return Response(data)
        id_number = ser.validated_data.get("id_number")
        try:
            _ = AdminUserInfo.objects.get(id_number=id_number)
            _.delete()
            data['status'] = True
            return Response(data)
        except Exception as e:
            print(e)
            return Response(data)


class AdminReUser(APIView):
    """
    超级管理员编辑管理人员
    """

    def post(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.data
        ser = AdminReUserSerializer(data=prams)
        if not ser.is_valid():
            print(ser.errors)
            return Response(data)

        openid = ser.validated_data.get("openid")

        if not check_is_superuser(openid):
            return Response(data)

        uid = ser.validated_data.get("uid")
        id_number = ser.validated_data.get("id_number")
        try:
            _ = AdminUserInfo.objects.get(id_number=id_number)
            admin_ownership = Community2LigaturesInfo.objects.get(pk=uid)
            _.admin_ownership = admin_ownership
            _.save()
            data['status'] = True
            return Response(data)
        except Exception as e:
            print(e)
            return Response(data)

        return Response(data)


class AdminFindUser(APIView):
    """
    超级管理员查找管理人员
    """

    def get(self, request, *args, **kwargs):
        data = {"status": False}
        prams = request.GET

        ser = AdminFindUserSerializer(data=prams)
        if not ser.is_valid():
            data['errors'] = ser.errors
            return Response(data)

        openid = ser.validated_data.get("openid")
        query = ser.validated_data.get("query")
        is_admin = ser.validated_data.get("is_admin")
        # address = ser.validated_data.get("address")
        page = ser.validated_data.get("page")
        size = ser.validated_data.get("size")

        if not check_is_superuser(openid):
            return Response(data)

        # result = BasicsUserInfo.objects.filter(
        #     Q(name__contains=query) | Q(id_number__contains=query) | Q(phone__contains=query))
        # if is_admin:
        #     category = int(is_admin)
        #     result = result.filter(Q(is_admin=is_admin))
        # else:
        #     result = result.filter(Q(is_admin=is_admin))
        result = AdminUserInfo.objects.exclude(is_admin=5)
        # result = AdminUserInfo.objects.filter(name=query)
        if is_admin:
            is_admin = int(is_admin)
            result = result.filter(Q(is_admin=is_admin))

        result = result.filter(Q(name__contains=query) | Q(id_number__contains=query) | Q(phone__contains=query))
        result = result.order_by("name")
        if result.exists():
            try:
                paginator = Paginator(result, size)

            except ValueError:
                paginator = Paginator(result, 10)
                size = 10
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:  # 不是数字
                posts = paginator.page(1)
            except EmptyPage:  # 超出页码范围
                posts = paginator.page(paginator.num_pages)
            count = paginator.count
            page = posts.number
            has_next = posts.has_next()
            size = len(posts)
            contacts = posts.object_list
            from django.core import serializers

            son_data = serializers.serialize("python", contacts, ensure_ascii=False)
            res = []
            for i in son_data:
                # print(i)
                pk = i.get("pk")
                fields = i.get("fields")

                _ = AdminUserInfo.objects.get(pk=pk).user_info

                fields['native'] = _.native
                fields['address'] = _.address
                fields['gender'] = _.gender
                fields['email'] = _.email
                fields['ownership'] = None

                if _.ownership:
                    fields['ownership'] = _.ownership.name

                fields['avatar_url'] = _.avatar_url.url

                fields['born'] = datetime.datetime.strftime(_.born, '%Y-%m-%d')
                fields['create_time'] = datetime.datetime.strftime(fields['create_time'], '%Y-%m-%d %H:%M:%S')

                del fields['admin_ownership']
                del fields['user_info']
                res.append(fields)

            data['data'] = res
            data['count'] = count
            data['size'] = size
            data['page'] = page
            data['has_next'] = has_next
        else:
            data['data'] = []
            data['count'] = 0
            data['has_next'] = False
        data['status'] = True
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
        id_number = prams.get("id_number").upper()
        isiting_reason = prams.get("visiting_reason")
        code = prams.get("code")

        health_code = myfile.get("health_code")
        travel_card = myfile.get("travel_card")
        cov_report = myfile.get("cov_report")

        appId = settings.APPID
        secret = settings.SECRET
        js_code = "0610C40w39fDRX2vGZ2w3vGjaR20C40C"
        url_ = f"https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={secret}&js_code={js_code}&grant_type=authorization_code"
        response_ = requests.get(url=url_)
        response_ = json.loads(response_.text)

        print("prams", prams)
        print("myfile", myfile)
