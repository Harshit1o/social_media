from django.urls import path
from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('explore/', views.ExploreView.as_view(), name='explore'),
    path('post_forms', views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/like/', views.like_post, name='like-post'),
    path('post/<int:pk>/comment/', views.add_comment, name='add-comment'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile_update/', views.profile_update, name='profile-update'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow-toggle'),
    path('register/', views.register, name='register'),
    path('accounts/profile/', views.profile_redirect , name='account-profile-redirect'),
    path('search/', views.search_user, name='search_user'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
]
