# quantable_app/views.py

from rest_framework import generics, permissions
from .models import Quantable, Vote
from .serializers import QuantableSerializer, VoteSerializer, CategorySerializer
from .enums import Category, CATEGORY_UNIT_MAPPING


class UnitListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        category_value = self.kwargs['category']
        category = Category(category_value)
        unit_enum = CATEGORY_UNIT_MAPPING[category]
        return [unit for unit in unit_enum]

class CategoryListView(generics.ListAPIView):
    queryset = [category for category in Category]
    serializer_class = CategorySerializer

class CreateQuantableView(generics.CreateAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class QuantableListView(generics.ListAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.AllowAny]


class QuantableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user)