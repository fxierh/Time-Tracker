from datetime import time

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q

# TODO: add DB indices to all models


def time_diff_in_seconds(start: time, end: time, end_next_day: bool) -> int:
    """
    Returns (end - start) in seconds, as an integer.

    Note: end_next_day is taken into account.

    :param start: datetime.time object
    :param end: datetime.time object
    :param end_next_day: bool
    """

    # Note: since start.second = end.second = 0, there is so no need to include them. 86400s = 1 day
    if end_next_day:
        return 86400 + (end.hour - start.hour) * 3600 + (end.minute - start.minute) * 60
    else:
        return (end.hour - start.hour) * 3600 + (end.minute - start.minute) * 60


class User(AbstractUser):
    """
    Custom user model, which extends Django's built-in AbstractUser model.

    All duration fields are in seconds.

    All added fields (i.e. non-existent in the built-in models) are calculated automatically.
    """

    # Make email field required.
    # Note: here the unique constraint is enforced on the backend and the db level.
    # However, a validation error will still be raised and shown in the frontend in case of duplicate.
    email = models.EmailField(max_length=254, unique=True)

    total_usable_time = models.PositiveBigIntegerField(default=0)
    total_study_time = models.PositiveBigIntegerField(default=0)
    total_work_time = models.PositiveBigIntegerField(default=0)

    stage_count = models.PositiveSmallIntegerField(default=0)
    day_count = models.PositiveSmallIntegerField(default=0)
    session_count = models.PositiveIntegerField(default=0)
    subject_count = models.PositiveIntegerField(default=0)

    # 0.0000 (0.00%) to 1.0000 (100.00%)
    time_usage_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    def __str__(self):
        return f"{self.username}"

    def save(self, *args, **kwargs):
        # Update user
        try:
            self.time_usage_ratio = self.total_study_time / self.total_usable_time
        except ZeroDivisionError:
            self.time_usage_ratio = 0

        super().save(*args, **kwargs)


class Day(models.Model):
    """
    All duration fields are in seconds.

    Default start time and day are only set in the form, otherwise the days model will always appear in migration,
    as the default field values always change.

    day_of_week, session_count, usable_time, study_time and time_usage_ratio are automatically calculated.

    When a day is saved of deleted, related fields in all models (day and others) are automatically updated.
    If a day is deleted, all associated sessions are deleted as well.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE)

    day = models.DateField()
    DAY_OF_WEEK_CHOICES = [
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'),
        ('7', 'Sunday'),
    ]
    day_of_week = models.SmallIntegerField(choices=DAY_OF_WEEK_CHOICES)
    session_count = models.PositiveSmallIntegerField(default=0)

    worktime = models.PositiveIntegerField(
        default=0,
        blank=True,
        help_text="May be completed later"
    )
    start = models.TimeField()
    end = models.TimeField(null=True, blank=True, help_text="May be completed later")
    end_next_day = models.BooleanField(default=False, null=True, blank=True, help_text="May be completed later")
    usable_time = models.PositiveIntegerField(default=0)
    study_time = models.PositiveIntegerField(default=0)

    # 0.0000 (0.00%) to 1.0000 (100.00%)
    time_usage_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    comment = models.TextField(max_length=100, null=True, blank=True, help_text="100 characters max")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'day'], name='user_day_uniqueness'),
            models.CheckConstraint(check=Q(time_usage_ratio__range=(0, 1)), name='day_time_usage_ratio_range')
        ]

    def __str__(self):
        return f"{self.day}" + f" {self.DAY_OF_WEEK_CHOICES[self.day_of_week - 1][-1]}" \
            if self.day_of_week else f"{self.day}"

    def save(self, *args, **kwargs):
        # Get previous field values
        day_obj = None
        try:
            day_obj = Day.objects.get(id=self.id)
            prev_work_time = day_obj.worktime
            prev_study_time = day_obj.study_time
            prev_session_count = day_obj.session_count
            prev_usable_time = day_obj.usable_time
            prev_stage = day_obj.stage
        except ObjectDoesNotExist:
            prev_work_time = 0
            prev_study_time = 0
            prev_session_count = 0
            prev_usable_time = 0
            prev_stage = None

        # Update day
        self.day_of_week = self.day.isoweekday()

        if self.start is not None and self.end is not None and self.end_next_day is not None:
            self.usable_time = time_diff_in_seconds(self.start, self.end, self.end_next_day) - self.worktime
        else:
            self.usable_time = 0

        try:
            self.time_usage_ratio = self.study_time / self.usable_time
        except ZeroDivisionError:
            self.time_usage_ratio = 0

        super().save(*args, **kwargs)

        # Update stage
        if self.stage == prev_stage or prev_stage is None:
            self.stage.total_work_time += self.worktime - prev_work_time
            self.stage.total_usable_time += self.usable_time - prev_usable_time
            self.stage.total_study_time += self.study_time - prev_study_time
            self.stage.session_count += self.session_count - prev_session_count

            # Increase day count only if the day is being created
            if day_obj is None:
                self.stage.day_count += 1
        else:
            prev_stage.total_usable_time -= prev_usable_time
            prev_stage.total_work_time -= prev_work_time
            prev_stage.total_study_time -= prev_study_time
            prev_stage.day_count -= 1
            prev_stage.session_count -= prev_session_count
            prev_stage.save()

            self.stage.total_work_time += self.worktime
            self.stage.total_usable_time += self.usable_time
            self.stage.total_study_time += self.study_time
            self.stage.session_count += self.session_count
            self.stage.day_count += 1

        self.stage.save()

    def delete(self, *args, **kwargs):
        # Delete all sessions associated
        for session in Session.objects.filter(day=self.id):
            session.delete(delete_day=True)

        # Update stage only when the day (not stage) is being deleted
        if not kwargs.pop('delete_stage', False):
            self.stage.total_usable_time -= self.usable_time
            self.stage.total_work_time -= self.worktime
            self.stage.total_study_time -= self.study_time
            self.stage.day_count -= 1
            self.stage.session_count -= self.session_count
            self.stage.save()

        super().delete(*args, **kwargs)


class Session(models.Model):
    """
    Default start time is set in the form, otherwise the day model will always appear in migration,
    as its default field value always changes.

    duration is in seconds, and is automatically calculated.

    When a session is saved of deleted, related fields in all models (session and others) are automatically updated.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.ForeignKey('Day', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)

    start = models.TimeField()
    end = models.TimeField(null=True, blank=True, help_text="May be completed later")
    end_next_day = models.BooleanField(default=False, null=True, blank=True, help_text="May be completed later")
    duration = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.day}, subject {self.subject}, " \
               f"from {self.start.strftime('%H:%M') if self.start else ''} " \
               f"to {self.end.strftime('%H:%M') if self.end else ''}"

    def save(self, *args, **kwargs):
        # Get previous field values
        session_obj = None
        try:
            session_obj = Session.objects.get(id=self.id)
            prev_duration = session_obj.duration
            prev_day = session_obj.day
            prev_subject = session_obj.subject
        except ObjectDoesNotExist:
            prev_duration = 0
            prev_day = None
            prev_subject = None

        # Update session
        if self.start is not None and self.end is not None and self.end_next_day is not None:
            self.duration = time_diff_in_seconds(self.start, self.end, self.end_next_day)
        else:
            self.duration = 0

        # Update day
        if self.day == prev_day or prev_day is None:
            self.day.study_time += self.duration - prev_duration

            # Increase session count only if the session is being created
            if session_obj is None:
                self.day.session_count += 1
        else:
            prev_day.study_time -= prev_duration
            prev_day.session_count -= 1
            prev_day.save()

            self.day.study_time += self.duration
            self.day.session_count += 1

        self.day.save()

        # Update subject
        if self.subject == prev_subject or prev_subject is None:
            self.subject.total_study_time += self.duration - prev_duration

            # Increase session count only if the session is being created
            if session_obj is None:
                self.subject.session_count += 1
        else:
            prev_subject.total_study_time -= prev_duration
            prev_subject.session_count -= 1
            prev_subject.save()

            self.subject.total_study_time += self.duration
            self.subject.session_count += 1

        self.subject.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update day only when the session (not day) is being deleted
        if not kwargs.pop('delete_day', False):
            self.day.session_count -= 1
            self.day.study_time -= self.duration
            self.day.save()

        # Update subject only when the session (not subject) is being deleted
        if not kwargs.pop('delete_subject', False):
            self.subject.session_count -= 1
            self.subject.total_study_time -= self.duration
            self.subject.save()

        super().delete(*args, **kwargs)


class Stage(models.Model):
    """
    day_count, session_count, time_usage_ratio & all duration fields of the stage model are automatically calculated.

    All duration fields of the stage model are in seconds.

    If a stage is deleted, all associated days are deleted as well.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, help_text="Easy to remember, 20 characters max")
    description = models.TextField(max_length=100, null=True, blank=True, help_text="100 characters max")

    day_count = models.PositiveSmallIntegerField(default=0)
    session_count = models.PositiveIntegerField(default=0)

    total_usable_time = models.PositiveBigIntegerField(default=0)
    total_study_time = models.PositiveBigIntegerField(default=0)
    total_work_time = models.PositiveBigIntegerField(default=0)

    # 0.0000 (0.00%) to 1.0000 (100.00%)
    time_usage_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='user_stage_uniqueness'),
        ]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # Get previous field values
        try:
            stage_obj = Stage.objects.get(id=self.id)
            prev_total_usable_time = stage_obj.total_usable_time
            prev_total_study_time = stage_obj.total_study_time
            prev_total_work_time = stage_obj.total_work_time
            prev_day_count = stage_obj.day_count
            prev_session_count = stage_obj.session_count
        except ObjectDoesNotExist:
            prev_total_usable_time = 0
            prev_total_study_time = 0
            prev_total_work_time = 0
            prev_day_count = 0
            prev_session_count = 0
            self.user.stage_count += 1

        # Update stage
        try:
            self.time_usage_ratio = self.total_study_time / self.total_usable_time
        except ZeroDivisionError:
            self.time_usage_ratio = 0

        super().save(*args, **kwargs)

        # Update user
        self.user.total_usable_time += self.total_usable_time - prev_total_usable_time
        self.user.total_study_time += self.total_study_time - prev_total_study_time
        self.user.total_work_time += self.total_work_time - prev_total_work_time
        self.user.day_count += self.day_count - prev_day_count
        self.user.session_count += self.session_count - prev_session_count
        self.user.save()

    def delete(self, *args, **kwargs):
        # Update user
        self.user.stage_count -= 1
        self.user.day_count -= self.day_count
        self.user.session_count -= self.session_count
        self.user.total_usable_time -= self.total_usable_time
        self.user.total_study_time -= self.total_study_time
        self.user.total_work_time -= self.total_work_time
        self.user.save()

        # Delete all days associated
        for day in Day.objects.filter(stage=self.id):
            day.delete(delete_stage=True)

        super().delete(*args, **kwargs)


class Subject(models.Model):
    """
    total_study_time is in seconds.

    total_study_time and session_count are automatically calculated.

    If a subject is deleted, all associated sessions are deleted as well.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, help_text="Easy to remember, 20 characters max")
    description = models.TextField(max_length=100, null=True, blank=True, help_text="100 characters max")
    total_study_time = models.PositiveBigIntegerField(default=0)
    session_count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='user_subject_uniqueness'),
        ]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        # Update user if subject created
        if not Subject.objects.filter(id=self.id).exists():
            self.user.subject_count += 1

        super().save(*args, **kwargs)

        self.user.save()

    def delete(self, *args, **kwargs):
        # Update user
        self.user.subject_count -= 1

        # The deletion of a subject triggers the deletion of all sessions associated
        sessions = Session.objects.filter(subject=self.id)

        # The user model will be saved later if the stage model update is triggered (function level cascade).
        # So if a subject contains no session and its deletion does not trigger an update of stage mode,
        # then the user has to be saved here.
        if not sessions:
            self.user.save()

        for session in sessions:
            session.delete(delete_subject=True)

        super().delete(*args, **kwargs)
