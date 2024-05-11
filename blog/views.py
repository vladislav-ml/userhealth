import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Avg, Count, F
from django.db.models.functions import Round
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (DetailView, FormView, ListView, TemplateView,
                                  View)

from .forms import CommentForm, ContactForm, StarForm
from .models import Category, Comment, MyPage, Post, Rating, Tag


class HomeView(ListView):
    """ Вывод главной страницы """
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.order_by('-created_at')[:7]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['categories'] = Category.objects.all().annotate(cnt=Count('post')).filter(cnt__gt=0).order_by('-cnt')
        context['main_page'] = get_object_or_404(MyPage, pk=1)
        context['health'] = Post.objects.filter(category_id=1).exclude(pk__in=self.get_queryset()).annotate(cnt_comment=Count('comment'))[:4]

        return context


class PostView(DetailView):
    """ Отдельный пост  """
    context_object_name = 'post'
    template_name = 'blog/single.html'

    def get_object(self):
        return get_object_or_404(Post.objects.annotate(cnt_comments=Count('comment', distinct=True)).annotate(cnt_tags=Count('tags', distinct=True)), slug=self.kwargs['slug'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.object.views = F('views') + 1
        self.object.save()
        self.object.refresh_from_db()
        context['related_posts'] = Post.objects.filter(category_id=self.object.category.id).exclude(pk=self.object.pk).order_by('-views')[:7]
        context['form'] = CommentForm()
        context['form_stars'] = StarForm()
        context['current_rating'] = Rating.objects.filter(post__slug=self.kwargs['slug']).aggregate(avg=Round(Avg('rating')))
        if context['current_rating'].get('avg'):
            context['current_rating'] = int(context['current_rating'].get('avg'))
        return context

    def post(self, request, slug):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('<h1>Forbidden</h1>')

        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['post'] = self.object
            data['user'] = self.request.user
            if request.POST.get('parent'):
                data['parent_id'] = int(request.POST.get('parent'))
            comment = Comment(**data)
            comment.save()
            messages.success(request, 'Коментарий успешно добавлен')
            return redirect(request.META['HTTP_REFERER'])
        else:
            context = self.get_context_data()
            context['form'] = form
        return render(request, 'blog/single.html', context)


class CategoryView(ListView):
    """ Вывод категории """
    context_object_name = 'posts'
    template_name = 'blog/category.html'
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['category'] = context['posts'][0].category
        return context

    def get_queryset(self):
        # return Category.objects.get(slug=self.kwargs['slug']).post_set.order_by('-created_at')
        return Post.objects.filter(category__slug=self.kwargs['slug']).order_by('-created_at').annotate(cnt_comment=Count('comment')).select_related('category')


class SearchView(ListView):
    """ Поиск на сайте """
    context_object_name = 'posts'
    template_name = 'blog/search.html'
    paginate_by = 6

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = f'Поиск по фразе «{self.request.GET.get("s")}»'
        context['s'] = f's={self.request.GET.get("s")}&'
        return context

    def get_queryset(self):
        return Post.objects.filter(title__icontains=self.request.GET.get('s')).annotate(cnt_comment=Count('comment')).order_by('-cnt_comment')


class TagView(ListView):
    """ Вывод статей по тегу """
    context_object_name = 'posts'
    template_name = 'blog/tag.html'
    paginate_by = 4

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        tag = Tag.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Статьи по тегу «{tag.title}»'
        return context

    def get_queryset(self):
        return Post.objects.filter(tags__slug=self.kwargs['slug']).annotate(cnt_comment=Count('comment'))


class ContactView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """ Контактная форма  """

    template_name = 'blog/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Контакты'}
    success_message = 'Сообщение успешно отправлено'

    def form_valid(self, form):
        data = form.cleaned_data
        resp = self.send_message_tg(data['name'], data['email'], data['content'])
        if resp.status_code == 200:
            return super().form_valid(form)
        else:
            form.add_error(None, 'Ошибка! Попробуйте позже.')
            return render(self.request, 'blog/contact.html', {'form': form, 'title': 'Контакты'})

    def send_message_tg(self, name, email, content):
        message = f'Сообщение с сайта: {self.request.META["HTTP_HOST"]}\nИмя: {name}\nEmail: {email}\nТекст:\n{content}'
        url_tg = f'https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage'
        data = {
            'chat_id': settings.TG_CHAT_ID,
            'text': message,
            'disable_web_page_preview': True,
        }
        response = requests.post(url_tg, data=data)
        return response


class AddRating(View):
    """ Добавление рейтинга статье """
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        print(f'x_forwarded_for- {x_forwarded_for}')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = StarForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                post_id=int(request.POST.get('post')),
                defaults={'rating': data['rating']}
            )
            return HttpResponse(status=200, content='Рейтинг обновлён')
        else:
            return HttpResponse(status=400)


class PageView(DetailView):
    """ Вывод отдельной страницы """
    model = MyPage
    template_name = 'blog/page.html'
    context_object_name = 'post'


class RobotsView(TemplateView):
    """ Вывод Robots.txt """
    template_name = 'robots.txt'
    content_type = 'text'
