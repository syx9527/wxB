from django.urls import path

from .views import *

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("login/", LoginView.as_view(), name="login"),
    path("re_login/", ReLogin.as_view(), name="re_login"),
    path("new_user_check_old_user/", NewUserCheckOldUser.as_view(), name="message"),
    path("message/", Message.as_view(), name="message"),
    path("get_user_info/", GetUserInfo.as_view(), name="get_user_info"),
    path("get_traffic_record/", GetTrafficRecord.as_view(), name="get_traffic_record"),
    path("check_code/", CheckCode.as_view(), name="message"),
    path("phone_message/", LoginByPhone.as_view(), name="phone_message"),
    path("get_code_session/", GetCode2Session.as_view(), name="get_code_session"),
    path("update_user/", UpdateUser.as_view(), name="update_user"),
    path("update_user_info/", UpdateUserInfo.as_view(), name="update_user_info"),
    path("get_audit_list/", AuditList.as_view(), name="get_audit_list"),
    path("audit_basics_user/", AuditBasicsUserInfo.as_view(), name="audit_basics_user"),
    path("get_community_list/", GetCommunityList.as_view(), name="get_community_list"),

    path("foreign_workers_registration/", ForeignWorkersRegistration.as_view(), name="foreign_workers_registration"),
    path("get_foreign_workers_registration/", GetForeignWorkersRegistration.as_view(),
         name="get_foreign_workers_registration"),
    path("re_foreign_workers_registration/", ReForeignWorkersRegistration.as_view(),
         name="re_foreign_workers_registration"),

    path("entry_exit_declaration/", EntryAndExitDeclaration.as_view(), name="entry_exit_declaration"),
    path("get_entry_exit_declaration/", GetEntryAndExitDeclaration.as_view(), name="get_entry_exit_declaration"),
    path("re_entry_exit_declaration/", ReEntryAndExitDeclaration.as_view(), name="re_entry_exit_declaration"),

    # 网格员对人员增删改查功能
    path("find_user/", FindUser.as_view(), name="find_user"),
    path("redit_user/", ReditUser.as_view(), name="redit_user"),
    path("del_user/", DelUser.as_view(), name="del_user"),
    # path("add_user/", AddUser.as_view(), name="add_user"),

    # path("get_audit_log/", GetAuditLog.as_view(), name="get_audit_log"),

    # 哨卡员专属功能
    path("sentry_post_find_user/", SentryPostFindUserByIdNumber.as_view(), name="sentry_post_find_user"),
    path("sentry_post_re_user/", SentryPostReUserByIdNumber.as_view(), name="sentry_post_re_user"),

    # 移动端超级管理员功能
    # 哨卡/社区增删改查
    path("add_community_ligatur/", AdminAddCommunity2Ligature.as_view(), name="add_community_ligatur"),
    path("del_community_ligatur/", AdminDelCommunity2Ligature.as_view(), name="del_community_ligatur"),
    path("re_community_ligatur/", AdminReCommunity2Ligature.as_view(), name="re_community_ligatur"),
    path("find_community_ligatur/", AdminFindCommunity2Ligature.as_view(), name="find_community_ligatur"),
    # 对各类管理员增删改查
    path("admin_add_user/", AdminAddUser.as_view(), name="admin_add_user"),
    path("admin_del_user/", AdminDelUser.as_view(), name="admin_del_user"),
    path("admin_re_user/", AdminReUser.as_view(), name="admin_re_user"),
    path("admin_find_user/", AdminFindUser.as_view(), name="admin_find_user"),

    path("user_exit/", UserExit.as_view(), name="user_exit"),

    path('token/', TokenAPIView.as_view()),
    path('get_token/', GetToken.as_view()),
    path('uploading', UploadingImageAPIView.as_view()),

    path("test/", Test.as_view(), name="test"),
    path("upload_img/", UploadImg.as_view(), name="test"),
]
