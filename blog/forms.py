from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Rating, Star


class ContactForm(forms.Form):
    name = forms.CharField(label='Ваше имя')
    email = forms.EmailField(label='Ваш email')
    content = forms.CharField(label='Сообщение', widget=forms.Textarea())


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'text': forms.Textarea({'placeholder': 'Ваш комментарий'}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if 'http://' in text or 'https://' in text:
            raise ValidationError('Недопустимые символы в сообщении.')
        return text


class StarForm(forms.ModelForm):
    rating = forms.ModelChoiceField(queryset=Star.objects.order_by('-pk'), widget=forms.RadioSelect())

    class Meta:
        model = Rating
        fields = ('rating',)
