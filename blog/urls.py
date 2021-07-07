from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path('<int:pk>/', views.PostDetail.as_view()),
    path('', views.PostList.as_view()),
]