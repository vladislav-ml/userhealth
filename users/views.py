from django.contrib.auth import get_user_model, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import LoginUserForm, ProfileUserForm, RegisterUserForm


class LoginUserView(SuccessMessageMixin, LoginView):
    template_name = 'users/login.html'
    form_class = LoginUserForm
    extra_context = {'title': 'Авторизация'}
    success_message = 'Успешно вошли в аккаунт'


class RegisterUserView(SuccessMessageMixin, CreateView):
    template_name = 'users/register.html'
    form_class = RegisterUserForm
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('auth:login')
    success_message = 'Успешно зарегистрировались'


class ProfileUserView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': 'Профиль'}
    success_message = 'Успешно обновлено'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('auth:profile')


class PasswordUserChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'users/password-change.html'
    success_url = reverse_lazy('auth:login')
    success_message = 'Пароль успешно обновлен'

    def form_valid(self, form):
        form.save()
        logout(self.request)
        return super().form_valid(form)


class DeleteUserView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = get_user_model()
    template_name = 'users/delete.html'
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Удаление аккаунта'}
    success_message = 'Аккаунт успешно удален'

    def get_object(self):
        return self.request.user
