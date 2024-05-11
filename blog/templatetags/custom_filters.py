from django.template.defaulttags import register


@register.filter
def add_class_error(field):
    class_el = ''
    if field.errors:
        class_el = 'block-error'
    return class_el


@register.filter
def show_word_review(number):
    html = ''
    if not number:
        html = 'отзывов нет'
    elif number % 10 == 1 and number != 11:
        html = f'{number} отзыв'
    elif number % 10 in [2, 3, 4] and number not in [12, 13, 14]:
        html = f'{number} отзыва'
    else: html = f'{number} отзывов'
    return html


@register.filter
def get_info_user(user):
    return user.first_name if user.first_name else user.email.split('@')[0]
