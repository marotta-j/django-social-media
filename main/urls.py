from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('sign-up/', views.sign_up, name='signup'),
    path('logout/', views.logout_view, name='logout_view'),
    path('create-post/', views.create_post, name='create_post'),
    path("<int:id>", views.post_view, name="post-view"),
    path("profile/<str:name>", views.profile_view, name="profile-view"),
    path("change_bio/", views.change_bio, name="change-bio"),
    path("like/", views.like_post, name="like-post"),
]