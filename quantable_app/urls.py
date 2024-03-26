# quantable_app/urls.py

from django.urls import path
from .views import (
    CreateQuantableView, QuantableListView, QuantableDetailView,
    VoteCreateView, VoteRetrieveUpdateDestroyView, CategoryListView, UnitListView, UserQuantablePreferenceView,
    # ChartTestView
)

urlpatterns = [
    path('quantables/create/', CreateQuantableView.as_view(), name='create_quantable'),
    path('quantables/list/', QuantableListView.as_view(), name='quantable_list'),
    path('quantables/detail/<int:pk>/', QuantableDetailView.as_view(), name='quantable_detail'),
    path('votes/create/', VoteCreateView.as_view(), name='create_vote'),
    path('votes/detail/<int:pk>/', VoteRetrieveUpdateDestroyView.as_view(), name='vote_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('units/<str:category>/', UnitListView.as_view(), name='unit_list'),
    path('preferences/update/', UserQuantablePreferenceView.as_view(), name='update_preference'),
    # path('chart-test/', ChartTestView.as_view(), name='chart_test'),
]