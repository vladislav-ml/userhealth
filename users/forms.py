from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       UserCreationForm)
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField

User = get_user_model()


class LoginUserForm(AuthenticationForm):
    # email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Введите email'}))
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'}))
    captcha = ReCaptchaField(label='')

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')


class RegisterUserForm(UserCreationForm):
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput())
    captcha = ReCaptchaField(label='')

    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')


class ProfileUserForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, label='Email', widget=forms.EmailInput())
    photo = forms.ImageField(label='Аватар', required=False, widget=forms.FileInput(), help_text='Размер изображения не более 100kB')
    sex = forms.CharField(label='Пол', required=False, widget=forms.RadioSelect(choices=User.Sex.choices))

    class Meta:
        model = get_user_model()
        fields = ('email', 'photo', 'first_name', 'last_name', 'sex')

    def clean_photo(self):
        photo = self.cleaned_data['photo']

        if photo and photo.size > settings.IMAGE_AVATAR_UPLOAD_LIMIT:
            raise ValidationError('Загруженный файл больше 100kB')
        return photo


class PasswordResetUserForm(PasswordResetForm):
    captcha = ReCaptchaField(label='')
