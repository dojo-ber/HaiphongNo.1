from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create/', views.PlaylistCreateView.as_view(), name='create_playlist'),
    path('overview/', views.PlaylistOverview.as_view(), name='overview_playlist'),
    path('detail/<int:pk>/', views.playlist_detail, name='detail_playlist'),
    path('delete/<int:pk>/', views.PlaylistDeleteView.as_view(), name='delete_playlist'),
    path('update/<int:pk>/', views.PlaylistUpdateView.as_view(), name='update_playlist'),
    path('toggle-like/', views.toggle_like_song, name='toggle_like'),

]


