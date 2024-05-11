from django.urls import include, path

from .views import PostAddView, PostEditDeleteView, PostListView

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('posts/', PostListView.as_view(), name='api_posts'),
    path('post_add/', PostAddView.as_view(), name='api_add'),
    path('post/<int:pk>/', PostEditDeleteView.as_view(), name='api_post'),
]
