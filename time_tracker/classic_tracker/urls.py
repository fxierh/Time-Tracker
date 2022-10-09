from django.urls import path

from .views import DashboardView, DayListView, DayUpdateView, DayDeleteView, DayCreateView, DayDetailView, \
    SessionCreateView, SessionListView, SessionUpdateView, SessionDeleteView, SessionDetailView, StageCreateView, \
    StageListView, StageUpdateView, StageDeleteView, SubjectCreateView, SubjectListView, \
    SubjectUpdateView, SubjectDeleteView, SubjectDetailView, StageDetailView

app_name = 'classic_tracker'

urlpatterns = [
    # TODO: cache dashboard page and provide a refresh button
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('create_day/', DayCreateView.as_view(), name='create_day'),
    # Day list is paginated in the backend and should not be cached
    path('list_day/', DayListView.as_view(), name='list_day'),
    path('update_day/<int:pk>/', DayUpdateView.as_view(), name='update_day'),
    path('delete_day/<int:pk>/', DayDeleteView.as_view(), name="delete_day"),
    path('day/<int:pk>/', DayDetailView.as_view(), name='detail_day'),

    path('create_session/', SessionCreateView.as_view(), name='create_session'),
    # Session list is paginated in the backend and should not be cached
    path('list_session/', SessionListView.as_view(), name='list_session'),
    path('update_session/<int:pk>/', SessionUpdateView.as_view(), name='update_session'),
    path('delete_session/<int:pk>/', SessionDeleteView.as_view(), name="delete_session"),
    path('session/<int:pk>/', SessionDetailView.as_view(), name='detail_session'),

    path('create_stage/', StageCreateView.as_view(), name='create_stage'),
    path('list_stage/', StageListView.as_view(), name='list_stage'),
    path('update_stage/<int:pk>/', StageUpdateView.as_view(), name='update_stage'),
    path('delete_stage/<int:pk>/', StageDeleteView.as_view(), name="delete_stage"),
    path('stage/<int:pk>/', StageDetailView.as_view(), name='detail_stage'),

    path('create_subject/', SubjectCreateView.as_view(), name='create_subject'),
    path('list_subject/', SubjectListView.as_view(), name='list_subject'),
    path('update_subject/<int:pk>/', SubjectUpdateView.as_view(), name='update_subject'),
    path('delete_subject/<int:pk>/', SubjectDeleteView.as_view(), name="delete_subject"),
    path('subject/<int:pk>/', SubjectDetailView.as_view(), name='detail_subject'),
]
