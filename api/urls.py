from django.urls import path

from .views import *

urlpatterns = [

    path("login/", LoginView.as_view(), name="login"),
    path("message/", Message.as_view(), name="message"),
    path("phone_message/", LoginByPhone.as_view(), name="phone_message"),
    path("get_code_session/", GetCode2Session.as_view(), name="get_code_session"),
    path("update_user/", UpdateUser.as_view(), name="update_user"),
    path("update_user_info/", UpdateUserInfo.as_view(), name="update_user_info"),
    path("get_audit_list/", AuditList.as_view(), name="get_audit_list"),
    path("get_audit_log/", AuditLog.as_view(), name="get_audit_log"),


    path("user_exit/", UserExit.as_view(), name="user_exit"),

    path('token', TokenAPIView.as_view()),
    path('uploading', UploadingImageAPIView.as_view()),

    path("test/", Test.as_view(), name="test"),
]
