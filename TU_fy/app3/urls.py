from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.PlaylistCreateView.as_view(), name='create_playlist'),
    path('overview/', views.PlaylistOverview.as_view(), name='overview_playlist'),
    path('detail/<int:playlist_id>/', views.playlist_detail, name='detail_playlist'),
    path('delete/<int:pk>/', views.PlaylistDeleteView.as_view(), name='delete_playlist'),
]
