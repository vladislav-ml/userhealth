import re

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.template.defaultfilters import slugify
from django.urls import reverse


def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return ''.join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Контент', blank=True)
    slug = models.SlugField(verbose_name='Url', unique=True)
    image = models.ImageField(verbose_name='Изображение', upload_to='category/', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Контент')
    image = models.ImageField(verbose_name='Изображение', upload_to='images/%Y/%m/%d/', blank=True)
    slug = models.SlugField(verbose_name='Url', unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    views = models.PositiveIntegerField(default=0, verbose_name='Кол-во просмотров')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    tags = models.ManyToManyField('Tag', verbose_name='Теги', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'slug': self.slug})

    # def get_reviews(self):
    #     return self.comment_set.filter(parent__isnull=True)

    def get_review_sort(self):
        comments_ordering = []
        comments = Comment.objects.filter(post__slug=self.slug).order_by(F('parent').asc(nulls_first=True), '-created_at').select_related('user').select_related('post')
        for comment in comments:
            if not comment.parent_id:
                comments_ordering.append({'id': comment.id, 'object': comment, 'child': []})
            else:
                for i, d in enumerate(comments_ordering):
                    if d['id'] == comment.parent_id:
                        comments_ordering[i]['child'].append([comment])
                        break
        return comments_ordering

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(translit_to_eng(self.title))
        description = ' '.join(self.content.split()[:30])
        description = re.sub(r'<[^>]+>', '', description)
        self.description = description
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']


class Tag(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(verbose_name='Url', unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст', help_text='Ссылки недопустимы в сообщении')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at', '-pk']


class MyPage(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Краткое описание')
    content = models.TextField(verbose_name='Контент', blank=True)
    slug = models.SlugField(verbose_name='Url', unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'


class Rating(models.Model):
    ip = models.CharField(verbose_name='IP', max_length=200)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='Пост')
    rating = models.ForeignKey('Star', on_delete=models.PROTECT, verbose_name='Рейтинг')

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'


class Star(models.Model):
    value_star = models.SmallIntegerField(verbose_name='Значение')

    def __str__(self):
        return str(self.value_star)

    class Meta:
        verbose_name = 'Рейтинг - Звезда'
        verbose_name_plural = 'Рейтинг - Звезды'
