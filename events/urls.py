from django.urls import path, reverse_lazy
from . import views

app_name='events'
urlpatterns = [
    path('', views.EventListView.as_view(), name='all'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event_detail'),
    path('event/create', views.EventCreateView.as_view(success_url=reverse_lazy('events:all')), name='event_create'),
    path('event/<int:pk>/update', views.EventUpdateView.as_view(success_url=reverse_lazy('events:all')), name='event_update'),
    path('event/<int:pk>/delete', views.EventDeleteView.as_view(success_url=reverse_lazy('events:all')), name='event_delete'),
    path('event_picture/<int:pk>', views.stream_file, name='event_picture'),
    path('event/<int:pk>/comment', views.CommentCreateView.as_view(), name='event_comment_create'),
    path('comment/<int:pk>/delete', views.CommentDeleteView.as_view(success_url=reverse_lazy('events:all')), name='event_comment_delete'),
    path('event/<int:pk>/donation', views.DonationCreateView.as_view(), name='event_donation_create'),
    path('donation/<int:pk>/delete', views.DonationDeleteView.as_view(success_url=reverse_lazy('events:all')), name='event_donation_delete'),
    path('event/<int:pk>/favorite', views.AddFavoriteView.as_view(), name='event_favorite'),
    path('event/<int:pk>/unfavorite', views.DeleteFavoriteView.as_view(), name='event_unfavorite'),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined
