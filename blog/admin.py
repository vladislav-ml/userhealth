from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import Category, Comment, MyPage, Post, Rating, Star, Tag


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = '__all__'


class CategoryAdmin(admin.ModelAdmin):
    save_as = True
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('id', 'title', 'slug', 'get_image', 'get_count_posts',)
    list_display_links = ('id', 'title')
    fields = ('title', 'slug', 'description', 'content', 'image', 'get_image',)
    readonly_fields = ('get_image',)

    def get_image(self, object):
        if object.image:
            return mark_safe(f'<img src="{ object.image.url }" alt="" width="80">')
        return '-'

    get_image.short_description = 'Миниатюра'

    def get_count_posts(self, object):
        return object.post_set.count()
    get_count_posts.short_description = 'Кол-во постов'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(cnt=Count('post')).order_by('-cnt')
        return qs


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    save_as = True
    save_on_top = True
    # prepopulated_fields = {'slug': ('title',)}
    list_display = ('id', 'title', 'category', 'created_at_display', 'get_image', 'views',)
    list_display_links = ('id', 'title',)
    search_fields = ('title', )
    list_filter = ('category', 'tags',)
    fields = ('title', 'content', 'category', 'tags', 'image', 'get_image', 'created_at', 'views',)
    readonly_fields = ('get_image', 'created_at', 'views',)

    def get_image(self, object):
        if object.image:
            return mark_safe(f'<img src="{ object.image.url }" alt="" width="80">')
        return '-'

    get_image.short_description = 'Миниатюра'

    def created_at_display(self, object):
        if object.created_at:
            return object.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_display.short_description = 'Дата создания'


class TagAdmin(admin.ModelAdmin):
    save_as = True
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('id', 'title', 'slug',)
    list_display_links = ('id', 'title',)


class MyPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}
    list_display = ('id', 'title', 'slug',)
    list_display_links = ('id', 'title', )
    fields = ('title', 'slug', 'description', 'content',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'post', 'parent',)
    list_display_links = ('id', 'user',)
    list_editable = ('parent',)


class RatingAdmin(admin.ModelAdmin):
    list_display = ('ip', 'post', 'rating',)
    list_display_links = ('ip', 'post',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(MyPage, MyPageAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Star)
