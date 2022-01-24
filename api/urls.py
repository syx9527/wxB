from django.urls import path

from .views import *

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("login/", LoginView.as_view(), name="login"),
    path("message/", Message.as_view(), name="message"),
    path("phone_message/", LoginByPhone.as_view(), name="phone_message"),
    path("get_code_session/", GetCode2Session.as_view(), name="get_code_session"),
    path("update_user/", UpdateUser.as_view(), name="update_user"),
    path("update_user_info/", UpdateUserInfo.as_view(), name="update_user_info"),
    path("get_audit_list/", AuditList.as_view(), name="get_audit_list"),
    path("get_community_list/", GetCommunityList.as_view(), name="get_community_list"),

    path("foreign_workers_registration/", ForeignWorkersRegistration.as_view(), name="foreign_workers_registration"),
    path("get_foreign_workers_registration/", GetForeignWorkersRegistration.as_view(),
         name="get_foreign_workers_registration"),
    path("re_foreign_workers_registration/", ReForeignWorkersRegistration.as_view(),
         name="re_foreign_workers_registration"),

    path("entry_exit_declaration/", EntryAndExitDeclaration.as_view(), name="entry_exit_declaration"),
    path("get_entry_exit_declaration/", GetEntryAndExitDeclaration.as_view(), name="get_entry_exit_declaration"),
    path("re_entry_exit_declaration/", ReEntryAndExitDeclaration.as_view(), name="re_entry_exit_declaration"),

    # path("get_audit_log/", GetAuditLog.as_view(), name="get_audit_log"),

    path("user_exit/", UserExit.as_view(), name="user_exit"),

    path('token', TokenAPIView.as_view()),
    path('uploading', UploadingImageAPIView.as_view()),

    path("test/", Test.as_view(), name="test"),
    path("upload_img/", UploadImg.as_view(), name="test"),
]
