# noinspection PyUnresolvedReferences
from classic_tracker.models import User, Stage, Day, Session, Subject
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model. """

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'total_usable_time',
            'total_study_time',
            'total_work_time',
            'stage_count',
            'day_count',
            'session_count',
            'subject_count',
        )
        read_only_fields = (
            'total_usable_time',
            'total_study_time',
            'total_work_time',
            'stage_count',
            'day_count',
            'session_count',
            'subject_count',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Overwrite the creation behavior so that encrypted password instead of plain password is saved. """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Overwrite the update behavior so that encrypted password instead of plain password is saved. """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate(self, data):
        """
        Validate password using Django's default password validation.
        This is done on the object (rather than field) level,
        as the UserAttributeSimilarityValidator requires the user object.
        """
        # Get user object & password
        user = get_user_model()(**data)
        password = data.get('password')

        # If password is provided, validate it using Django's default password validators and catch exceptions
        if password:
            errors = dict()
            try:
                validate_password(password=password, user=user)
            except ValidationError as e:
                errors['password'] = list(e.messages)

            # Raise password validation error
            # By default this exception results in a response with the HTTP status code "400 Bad Request"
            if errors:
                raise serializers.ValidationError(errors)

        # Return validated data
        return data


class StageSerializer(serializers.ModelSerializer):
    """Serializer for the stage model. """

    class Meta:
        model = Stage
        fields = (
            'id',
            'name',
            'description',
            'day_count',
            'session_count',
            'total_usable_time',
            'total_study_time',
            'total_work_time',
            'time_usage_ratio',
        )
        read_only_fields = (
            'id',
            'day_count',
            'session_count',
            'total_usable_time',
            'total_study_time',
            'total_work_time',
            'time_usage_ratio',
        )


class DaySerializer(serializers.ModelSerializer):
    """Serializer for the day model. """

    class Meta:
        model = Day
        fields = (
            'id',
            'stage',
            'day',
            'day_of_week',
            'session_count',
            'worktime',
            'start',
            'end',
            'end_next_day',
            'usable_time',
            'study_time',
            'time_usage_ratio',
            'comment',
        )
        read_only_fields = (
            'id',
            'day_of_week',
            'session_count',
            'usable_time',
            'study_time',
            'time_usage_ratio',
        )

    def validate_stage(self, value):
        """Field-level validation which makes sure that the related stage belongs to the current user. """
        # value is an object of the related field class
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("The related field does not belong to the current user.")

        return value


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for the session model. """

    class Meta:
        model = Session
        fields = (
            'id',
            'day',
            'subject',
            'start',
            'end',
            'end_next_day',
            'duration',
        )
        read_only_fields = (
            'id',
            'duration',
        )

    def validate_day(self, value):
        """Field-level validation which makes sure that the related day belongs to the current user. """
        # value is an object of the Day class
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("The related field does not belong to the current user.")

        return value

    def validate_subject(self, value):
        """Field-level validation which makes sure that the related subject belongs to the current user. """
        # value is an object of the Subject class
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("The related field does not belong to the current user.")

        return value


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for the subject model. """

    class Meta:
        model = Subject
        fields = (
            'id',
            'name',
            'description',
            'total_study_time',
            'session_count',
        )
        read_only_fields = (
            'id',
            'total_study_time',
            'session_count',
        )
