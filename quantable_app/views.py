# quantable_app/views.py

from rest_framework import generics, permissions, request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from . import serializers
from .models import Quantable, Vote, UserQuantablePreference
from .serializers import QuantableSerializer, VoteSerializer, CategorySerializer, UserQuantablePreferenceSerializer
from .enums import Category, CATEGORY_UNIT_MAPPING
from .unit_conversions import UNIT_CONVERSION_FUNCTIONS


import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response


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
        category = serializer.validated_data['category']
        available_units = serializer.validated_data['available_units']
        default_unit = serializer.validated_data['default_unit']
        creator = self.request.user
        creator_name = self.request.session.get('preferred_name', 'Unknown')

        unit_enum = CATEGORY_UNIT_MAPPING.get(Category(category))
        if unit_enum:
            valid_units = [unit.value for unit in unit_enum]
            if default_unit not in valid_units:
                raise serializers.ValidationError("Invalid default unit for the chosen category.")
            if not all(unit in valid_units for unit in available_units):
                raise serializers.ValidationError("Invalid available units for the chosen category.")

        serializer.save(creator=creator, creator_name=creator_name)


class QuantableListView(generics.ListAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Get the sorting option from the request query parameters
        sort_option = request.query_params.get('sort', 'newest')

        # Apply sorting based on the selected option
        if sort_option == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_option == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_option == 'total_votes':
            queryset = queryset.order_by('-vote_count')

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        for quantable_data in data:
            quantable = Quantable.objects.get(id=quantable_data['id'])
            user = request.user

            if user.is_authenticated:
                preference, _ = UserQuantablePreference.objects.get_or_create(user=user, quantable=quantable)
                preferred_unit = preference.preferred_unit
            else:
                preferred_unit = quantable.default_unit

            quantable_data['preferred_unit'] = preferred_unit or quantable.default_unit
            quantable_data['freedman_diaconis_bins'] = quantable.freedman_diaconis_bins()

            # Identify fields that should undergo unit conversion
            fields_for_conversion = [
                'vote_average', 'vote_median', 'vote_stddev',
                'vote_q1', 'vote_q3', 'vote_iqr', 'vote_min', 'vote_max'
            ]

            if preferred_unit and preferred_unit != quantable.default_unit:
                conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(quantable.category))
                if conversion_function:
                    for key in fields_for_conversion:
                        value = quantable_data.get(key)
                        if value is not None:
                            quantable_data[key] = conversion_function(value, quantable.default_unit, preferred_unit)

        return Response(data)


class QuantableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        user = request.user
        if user.is_authenticated:
            preference, _ = UserQuantablePreference.objects.get_or_create(user=user, quantable=instance)
            preferred_unit = preference.preferred_unit
            user_vote = Vote.objects.filter(user=user, quantable=instance).first()
            if user_vote:
                data['user_vote'] = user_vote.value
                if preferred_unit and preferred_unit != instance.default_unit:
                    conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(instance.category))
                    if conversion_function:
                        data['user_vote'] = conversion_function(user_vote.value, instance.default_unit, preferred_unit)
        else:
            preferred_unit = instance.default_unit

        # Identify fields that should undergo unit conversion
        fields_for_conversion = [
            'vote_values', 'vote_average', 'vote_median', 'vote_stddev',
            'vote_q1', 'vote_q3', 'vote_iqr', 'vote_min', 'vote_max'
        ]

        if preferred_unit and preferred_unit != instance.default_unit:
            conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(instance.category))
            if conversion_function:
                converted_data = {}
                for key, value in data.items():
                    if key in fields_for_conversion:
                        if key == 'vote_values':
                            converted_data[key] = [conversion_function(vote, instance.default_unit, preferred_unit) for
                                                   vote in value]
                        elif value is not None:  # Check if the value is not None before conversion
                            converted_data[key] = conversion_function(value, instance.default_unit, preferred_unit)
                        else:
                            converted_data[key] = value
                    else:
                        converted_data[key] = value
                data = converted_data

        data['preferred_unit'] = preferred_unit or instance.default_unit
        data['available_units'] = [unit for unit in instance.available_units if unit != instance.default_unit]
        data['freedman_diaconis_bins'] = instance.freedman_diaconis_bins()

        ninety_percent_range = instance.ninety_percent_vote_range()
        if ninety_percent_range:
            nmin, nmax = ninety_percent_range
            data['ninety_percent_vote_range'] = {
                'nmin': nmin,
                'nmax': nmax,
                'statement': f"90% of our community think that the correct answer is somewhere between {nmin:.2f} and {nmax:.2f} {preferred_unit or instance.default_unit}."
            }
        else:
            data['ninety_percent_vote_range'] = None

        return Response(data)


class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        quantable = serializer.validated_data['quantable']
        preferred_unit = self.request.data.get('preferred_unit')
        user = self.request.user

        try:
            vote = Vote.objects.get(quantable=quantable, user=user)
            # Update existing vote
            if preferred_unit and preferred_unit != quantable.default_unit:
                conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(quantable.category))
                if conversion_function:
                    value = serializer.validated_data['value']
                    converted_value = conversion_function(value, preferred_unit, quantable.default_unit)
                    vote.value = converted_value
                    vote.save()
                else:
                    raise ValidationError("Unit conversion not supported for this category.")
            else:
                vote.value = serializer.validated_data['value']
                vote.save()
        except Vote.DoesNotExist:
            # Create new vote
            if preferred_unit and preferred_unit != quantable.default_unit:
                conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(quantable.category))
                if conversion_function:
                    value = serializer.validated_data['value']
                    converted_value = conversion_function(value, preferred_unit, quantable.default_unit)
                    serializer.save(user=user, value=converted_value)
                else:
                    raise ValidationError("Unit conversion not supported for this category.")
            else:
                serializer.save(user=user)


class VoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        quantable = instance.quantable
        preferred_unit = request.data.get('preferred_unit')

        if preferred_unit and preferred_unit != quantable.unit:
            conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(quantable.category))
            if conversion_function:
                value = request.data.get('value')
                converted_value = conversion_function(value, preferred_unit, quantable.unit)
                serializer = self.get_serializer(instance, data={'value': converted_value}, partial=True)
            else:
                raise serializers.ValidationError("Unit conversion not supported for this category.")
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class UserQuantablePreferenceView(generics.UpdateAPIView):
    queryset = UserQuantablePreference.objects.all()
    serializer_class = UserQuantablePreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        quantable_id = request.data.get('quantable_id')
        preferred_unit = request.data.get('preferred_unit')

        preference, _ = UserQuantablePreference.objects.get_or_create(user=request.user, quantable_id=quantable_id)
        preference.preferred_unit = preferred_unit
        preference.save()

        return Response({'detail': 'Preference updated successfully'})


# class ChartTestView(APIView):
#     def get(self, request):
#         # Generate sample vote data
#         np.random.seed(0)  # Set a fixed seed for reproducibility
#         num_votes = 1000
#         mean_vote = 50
#         std_dev = 15
#         vote_data = np.random.normal(mean_vote, std_dev, num_votes)
#
#         # Calculate Freedman-Diaconis bins
#         iqr = np.subtract(*np.percentile(vote_data, [75, 25]))
#         bin_width = 2 * iqr / (len(vote_data) ** (1/3))
#         num_bins = int(np.ceil((vote_data.max() - vote_data.min()) / bin_width))
#         bins = np.linspace(vote_data.min(), vote_data.max(), num_bins + 1)
#
#         # Calculate bin counts and percentages
#         bin_counts, _ = np.histogram(vote_data, bins=bins)
#         bin_percentages = bin_counts / len(vote_data) * 100
#
#         # Format the data for the BoxPlotWithDensity component
#         chart_data = {
#             'freedman_diaconis_bins': [
#                 {
#                     'bin_min': bins[i],
#                     'bin_max': bins[i + 1],
#                     'count': int(bin_counts[i]),
#                     'percentage': bin_percentages[i]
#                 }
#                 for i in range(len(bins) - 1)
#             ],
#             'vote_average': np.mean(vote_data),
#             'vote_median': np.median(vote_data),
#             'vote_stddev': np.std(vote_data),
#             'vote_q1': np.percentile(vote_data, 25),
#             'vote_q3': np.percentile(vote_data, 75),
#             'vote_iqr': iqr,
#             'vote_min': np.min(vote_data),
#             'vote_max': np.max(vote_data),
#             'vote_skewness': 0  # Skewness is 0 for normally distributed data
#         }
#
#         return Response(chart_data)