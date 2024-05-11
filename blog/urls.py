from django.urls import path

from .views import (AddRating, CategoryView, ContactView, HomeView, PageView,
                    PostView, RobotsView, SearchView, TagView)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('robots.txt', RobotsView.as_view()),
    path('search/', SearchView.as_view(), name='search'),
    path('rating/', AddRating.as_view(), name='rating'),
    path('tag/<str:slug>/', TagView.as_view(), name='tag'),
    path('cat/<str:slug>/', CategoryView.as_view(), name='category'),
    path('page/contact/', ContactView.as_view(), name='contact'),
    path('page/<str:slug>/', PageView.as_view(), name='page'),
    path('<str:slug>/', PostView.as_view(), name='post'),
]
