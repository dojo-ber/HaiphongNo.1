from django.urls import path
from . import views

urlpatterns = [
    path("create_playlist", views.PlayListCreateView.as_view(), name="create_playlist"),
    path("overview_playlist", views.PlayListOverview.as_view(), name="overview_playlist"),
    path("detail_playlist/<int:playlist_id>", views.playlist_detail, name="detail_playlist")
]
