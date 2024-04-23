# quantable_app/views.py

from rest_framework import generics, permissions, request, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import APIView

from . import serializers
from .models import Quantable, Vote, UserQuantablePreference
from .serializers import QuantableSerializer, VoteSerializer, CategorySerializer, UserQuantablePreferenceSerializer, \
    QuantablePairSerializer
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

    def create(self, request, *args, **kwargs):
        quantable_data = request.data
        creator = self.request.user
        creator_name = self.request.session.get('preferred_name', 'Unknown')

        if 'pair_id' in quantable_data:
            # Create a quantable pair
            pair_id = quantable_data['pair_id']
            min_quantable_data = quantable_data['min_quantable']
            max_quantable_data = quantable_data['max_quantable']

            min_quantable_serializer = self.get_serializer(data=min_quantable_data)
            min_quantable_serializer.is_valid(raise_exception=True)
            min_quantable = min_quantable_serializer.save(
                creator=creator,
                creator_name=creator_name,
                pair_id=pair_id,
                is_min=True
            )

            max_quantable_serializer = self.get_serializer(data=max_quantable_data)
            max_quantable_serializer.is_valid(raise_exception=True)
            max_quantable = max_quantable_serializer.save(
                creator=creator,
                creator_name=creator_name,
                pair_id=pair_id,
                is_min=False
            )

            response_data = {
                'pair_id': pair_id,
                'min_quantable': min_quantable_serializer.data,
                'max_quantable': max_quantable_serializer.data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            # Create a single quantable
            serializer = self.get_serializer(data=quantable_data)
            serializer.is_valid(raise_exception=True)
            quantable = serializer.save(
                creator=creator,
                creator_name=creator_name
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuantableListView(generics.ListAPIView):
    queryset = Quantable.objects.all()
    serializer_class = QuantableSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        try:
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

            quantable_pairs = {}
            individual_quantables = []

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

                if quantable_data['pair_id']:
                    pair_id = quantable_data['pair_id']
                    if pair_id not in quantable_pairs:
                        quantable_pairs[pair_id] = {'min_quantable': None, 'max_quantable': None}
                    if quantable_data['is_min']:
                        quantable_pairs[pair_id]['min_quantable'] = quantable_data
                    else:
                        quantable_pairs[pair_id]['max_quantable'] = quantable_data
                else:
                    individual_quantables.append(quantable_data)

            # Prepare the response data
            response_data = []

            for pair_id, pair_data in quantable_pairs.items():
                min_quantable = pair_data['min_quantable']
                max_quantable = pair_data['max_quantable']
                if min_quantable and max_quantable:
                    response_data.append({
                        'pair_id': pair_id,
                        'min_quantable': min_quantable,
                        'max_quantable': max_quantable,
                        'type': 'pair'
                    })

            response_data.extend(individual_quantables)

            return Response(response_data)
        except ValueError as e:
            # Handle the ValueError exception
            error_message = str(e)
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


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


class QuantablePairDetailView(generics.RetrieveAPIView):
    serializer_class = QuantablePairSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        pair_id = self.kwargs['pair_id']
        pair_quantables = Quantable.objects.filter(pair_id=pair_id)
        if pair_quantables.count() != 2:
            raise NotFound("Quantable pair not found.")
        return pair_quantables

    def retrieve(self, request, *args, **kwargs):
        pair_quantables = self.get_object()
        min_quantable = pair_quantables.filter(is_min=True).first()
        max_quantable = pair_quantables.filter(is_min=False).first()

        if min_quantable is None or max_quantable is None:
            return Response({'detail': 'Quantable pair not found.'}, status=status.HTTP_404_NOT_FOUND)

        preferred_unit = request.query_params.get('preferred_unit')
        print(f"Preferred unit from request: {preferred_unit}")

        user = request.user
        if user.is_authenticated:
            min_preference, _ = UserQuantablePreference.objects.get_or_create(user=user, quantable=min_quantable)
            min_preference.preferred_unit = preferred_unit
            min_preference.save()

            max_preference, _ = UserQuantablePreference.objects.get_or_create(user=user, quantable=max_quantable)
            max_preference.preferred_unit = preferred_unit
            max_preference.save()

        min_quantable_data = QuantableSerializer(min_quantable).data
        max_quantable_data = QuantableSerializer(max_quantable).data

        min_user_vote = min_quantable.vote_set.filter(user=user).first()
        max_user_vote = max_quantable.vote_set.filter(user=user).first()

        if min_user_vote:
            min_quantable_data['user_vote'] = min_user_vote.value
        else:
            min_quantable_data['user_vote'] = None

        if max_user_vote:
            max_quantable_data['user_vote'] = max_user_vote.value
        else:
            max_quantable_data['user_vote'] = None

        min_quantable_data['freedman_diaconis_bins'] = min_quantable.freedman_diaconis_bins()
        max_quantable_data['freedman_diaconis_bins'] = max_quantable.freedman_diaconis_bins()

        if preferred_unit and preferred_unit != min_quantable.default_unit:
            conversion_function = UNIT_CONVERSION_FUNCTIONS.get(Category(min_quantable.category))
            if conversion_function:
                self.apply_unit_conversion(min_quantable_data, conversion_function, min_quantable.default_unit, preferred_unit)
                self.apply_unit_conversion(max_quantable_data, conversion_function, max_quantable.default_unit, preferred_unit)

        min_quantable_data['preferred_unit'] = preferred_unit or min_quantable.default_unit
        max_quantable_data['preferred_unit'] = preferred_unit or max_quantable.default_unit

        serializer = self.get_serializer({
            'min_quantable': min_quantable_data,
            'max_quantable': max_quantable_data
        })

        print(f"Response data: {serializer.data}")

        return Response(serializer.data)

    def apply_unit_conversion(self, quantable_data, conversion_function, default_unit, preferred_unit):
        fields_for_conversion = [
            'vote_average', 'vote_median', 'vote_stddev',
            'vote_q1', 'vote_q3', 'vote_iqr', 'vote_min', 'vote_max'
        ]

        for key in fields_for_conversion:
            value = quantable_data.get(key)
            if value is not None:
                converted_value = conversion_function(value, default_unit, preferred_unit)
                quantable_data[key] = round(converted_value, 2)  # Round to 2 decimal places

        if 'user_vote' in quantable_data and quantable_data['user_vote'] is not None:
            converted_user_vote = conversion_function(quantable_data['user_vote'], default_unit, preferred_unit)
            quantable_data['user_vote'] = round(converted_user_vote, 2)  # Round to 2 decimal places

        for bin_data in quantable_data['freedman_diaconis_bins']:
            bin_min = conversion_function(bin_data['bin_min'], default_unit, preferred_unit)
            bin_max = conversion_function(bin_data['bin_max'], default_unit, preferred_unit)
            bin_data['bin_min'] = round(bin_min, 2)  # Round to 2 decimal places
            bin_data['bin_max'] = round(bin_max, 2)  # Round to 2 decimal places


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
