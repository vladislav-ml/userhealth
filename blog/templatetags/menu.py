from django import template
from django.core.cache import cache
from django.db.models import Count

from blog.models import Category

register = template.Library()


@register.inclusion_tag('inc/_menu.html', takes_context=True)
def show_menu(context, number_menu=1):
    request = context['request']
    category = cache.get('menu-category')
    if not category:
        category = Category.objects.annotate(cnt=Count('post')).filter(cnt__gt=0).order_by('-cnt')[:5]
        cache.set('menu-category', category, 60 * 10)
    return {'category': category, 'number_menu': number_menu, 'request': request}
