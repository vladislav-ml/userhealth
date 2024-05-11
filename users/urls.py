from django.contrib.auth.views import (LogoutView, PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path, reverse_lazy

from .forms import PasswordResetUserForm
from .views import (DeleteUserView, LoginUserView, PasswordUserChangeView,
                    ProfileUserView, RegisterUserView)

app_name = 'users'

urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('profile/', ProfileUserView.as_view(), name='profile'),
    path('password_change/', PasswordUserChangeView.as_view(), name='password-change'),

    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html', email_template_name='users/password_reset_email.html', success_url=reverse_lazy('auth:password_reset_done'), form_class=PasswordResetUserForm), name='password_reset'),

    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html', success_url=reverse_lazy('auth:password_reset_complete')), name='password_reset_confirm'),

    path('password_reset/complete/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    path('delete/', DeleteUserView.as_view(), name='delete')
]
