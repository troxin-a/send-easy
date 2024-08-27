from django.urls import path

from django.contrib.auth.views import LogoutView

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
    path("confirm-email/<str:token>/", views.confirm_email, name="confirm_email"),
    path("info/", views.info_confirm_email, name="info"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("password-change/", views.CustomPasswordChangeView.as_view(), name="password_change"),
    path("password-change-done/", views.CustomPasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password-reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset-done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset-complete/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("list/", views.UserListView.as_view(), name="user_list"),
    path("change-user-activity/<int:pk>", views.change_user_activity, name="change_user_activity"),
]
