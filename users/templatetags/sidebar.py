from django import template
from django.core.cache import cache

from blog.models import Post

register = template.Library()


@register.inclusion_tag(filename='users/inc/_sidebar.html',)
def get_sidebar():
    posts = cache.get('sidebar_posts')
    if not posts:
        posts = Post.objects.order_by('-created_at')[:2]
        cache.set('sidebar_posts', posts, 60 * 2)
    return {'posts': posts}
