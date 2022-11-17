from django.db import transaction
from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from rest_framework import generics, authentication, permissions, viewsets

from .serializers import UserSerializer, StageSerializer, DaySerializer, SessionSerializer, SubjectSerializer
# noinspection PyUnresolvedReferences
from classic_tracker.models import Stage, Day, Session, Subject


class CreateUserView(generics.CreateAPIView):
    """Endpoint for creating a non-admin user. """
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(description="Endpoint for retrieving the current user's profile."),
    put=extend_schema(description="Endpoint for updating the current user's profile."),
    patch=extend_schema(description="Endpoint for partially updating the current user's profile."),
    delete=extend_schema(description="Endpoint for deleting the current user's account.")
)
class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoints for getting/updating/deleting the authenticated user. """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Returns an object instance used for detail views. """
        return self.request.user


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'names',
                OpenApiTypes.STR,
                description='Comma separated list of stage names. No space after comma.',
            ),
        ],
        description='Endpoint that lists all stages of the current user.',
    ),
    create=extend_schema(description='Endpoint for creating one or multiple stages for the current user.'),
    retrieve=extend_schema(description='Endpoint for retrieving a stage of the current user.'),
    update=extend_schema(description='Endpoint for updating a stage of the current user.'),
    partial_update=extend_schema(description='Endpoint for partially updating a stage of the current user.'),
    destroy=extend_schema(description='Endpoint for deleting a stage of the current user.')
)
@method_decorator(transaction.atomic, name='dispatch')
class StageViewSet(viewsets.ModelViewSet):
    """Endpoints operating on the current user's stages. """
    serializer_class = StageSerializer
    queryset = Stage.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """If an array of objects is passed, set many=True in serializer kwargs. """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        """Only stages of the current user are listed. Also supports filtering by name. """
        queryset = self.queryset
        names = self.request.query_params.get('names')
        if names:
            queryset = queryset.filter(name__in=names.split(','))
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Overwrite the serializer's saving behavior by passing an additional argument to .save(). """
        serializer.save(user=self.request.user)


@extend_schema_view(
    # Extend schema for the list method of the viewset
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'dates',
                OpenApiTypes.STR,
                description='Comma separated list of dates, e.g. 2022-1-1,2022-1-2. No space after comma.',
            ),
            OpenApiParameter(
                'stages',
                OpenApiTypes.STR,
                description='Comma separated list of related stage ids. No space after comma.',
            ),
        ],
        description='Endpoint that lists all days of the current user.'
    ),
    create=extend_schema(description='Endpoint for creating one or multiple days for the current user.'),
    retrieve=extend_schema(description='Endpoint for retrieving a day of the current user.'),
    update=extend_schema(description='Endpoint for updating a day of the current user.'),
    partial_update=extend_schema(description='Endpoint for partially updating a day of the current user.'),
    destroy=extend_schema(description='Endpoint for deleting a day of the current user.')
)
@method_decorator(transaction.atomic, name='dispatch')
class DayViewSet(viewsets.ModelViewSet):
    """Endpoints operating on the current user's days. """
    serializer_class = DaySerializer
    queryset = Day.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """If an array of objects is passed, set many=True in serializer kwargs. """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        """Only stages of the current user are listed. Also supports filtering by date and/or stage id. """
        queryset = self.queryset
        dates = self.request.query_params.get('dates')
        stages = self.request.query_params.get('stages')
        if dates:
            queryset = queryset.filter(day__in=dates.split(','))
        if stages:
            queryset = queryset.filter(stage__in=stages.split(','))
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Overwrite the serializer's saving behavior by passing an additional argument to .save(). """
        serializer.save(user=self.request.user)


@extend_schema_view(
    # Extend schema for the list method of the viewset
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'days',
                OpenApiTypes.STR,
                description='Comma separated list of day ids. No space after comma.',
            ),
            OpenApiParameter(
                'subjects',
                OpenApiTypes.STR,
                description='Comma separated list of subject ids. No space after comma.',
            ),
        ],
        description='Endpoint that lists all sessions of the current user.'
    ),
    create=extend_schema(description='Endpoint for creating one or multiple sessions for the current user.'),
    retrieve=extend_schema(description='Endpoint for retrieving a session of the current user.'),
    update=extend_schema(description='Endpoint for updating a session of the current user.'),
    partial_update=extend_schema(description='Endpoint for partially updating a session of the current user.'),
    destroy=extend_schema(description='Endpoint for deleting a session of the current user.')
)
@method_decorator(transaction.atomic, name='dispatch')
class SessionViewSet(viewsets.ModelViewSet):
    """Endpoints operating on the current user's sessions. """
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """If an array of objects is passed, set many=True in serializer kwargs. """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        """Only stages of the current user are listed. Also supports filtering by day and/or subject id. """
        queryset = self.queryset
        days = self.request.query_params.get('days')
        subjects = self.request.query_params.get('subjects')
        if days:
            queryset = queryset.filter(day__in=days.split(','))
        if subjects:
            queryset = queryset.filter(subject__in=subjects.split(','))
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Overwrite the serializer's saving behavior by passing an additional argument to .save(). """
        serializer.save(user=self.request.user)


@extend_schema_view(
    # Extend schema for the list method of the viewset
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'names',
                OpenApiTypes.STR,
                description='Comma separated list of subject names. No space after comma.',
            ),
        ],
        description='Endpoint that lists all subjects of the current user.'
    ),
    create=extend_schema(description='Endpoint for creating one or multiple subjects for the current user.'),
    retrieve=extend_schema(description='Endpoint for retrieving a subject of the current user.'),
    update=extend_schema(description='Endpoint for updating a subject of the current user.'),
    partial_update=extend_schema(description='Endpoint for partially updating a subject of the current user.'),
    destroy=extend_schema(description='Endpoint for deleting a subject of the current user.')
)
@method_decorator(transaction.atomic, name='dispatch')
class SubjectViewSet(viewsets.ModelViewSet):
    """Endpoints operating on the current user's stages. """
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """If an array of objects is passed, set many=True in serializer kwargs. """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        """Only stages of the current user are listed. Also supports filtering by name. """
        queryset = self.queryset
        names = self.request.query_params.get('names')
        if names:
            queryset = queryset.filter(name__in=names.split(','))
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Overwrite the serializer's saving behavior by passing an additional argument to .save(). """
        serializer.save(user=self.request.user)
