# quantable_app/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from . import serializers
from .models import Quantable, Vote
from .serializers import QuantableSerializer, VoteSerializer, CategorySerializer
from .enums import Category, CATEGORY_UNIT_MAPPING
from .unit_conversions import UNIT_CONVERSION_FUNCTIONS


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


# quantable_app/views.py

class QuantableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        preferred_unit = request.query_params.get('preferred_unit')
        if preferred_unit and preferred_unit != instance.unit:
            conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(instance.category))
            if conversion_function:
                converted_data = {}
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        converted_data[key] = conversion_function(value, instance.unit, preferred_unit)
                    elif key == 'vote_values':
                        converted_data[key] = [conversion_function(vote, instance.unit, preferred_unit) for vote in value]
                    else:
                        converted_data[key] = value
                data = converted_data

        return Response(data)


class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        quantable = serializer.validated_data['quantable']
        preferred_unit = self.request.data.get('preferred_unit')

        if preferred_unit and preferred_unit != quantable.unit:
            conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(quantable.category))
            if conversion_function:
                value = serializer.validated_data['value']
                converted_value = conversion_function(value, preferred_unit, quantable.unit)
                serializer.save(user=self.request.user, value=converted_value)
            else:
                raise serializers.ValidationError("Unit conversion not supported for this category.")
        else:
            serializer.save(user=self.request.user)


class VoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user)