from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Day, Session, Stage, Subject, User

# TODO: define field order


@admin.register(User)
class UserAdminExtended(UserAdmin):
    # Note:
    # list_display controls which fields are displayed on the change list page of the admin,
    # instead of the __str__() representation of each object.
    # fieldsets is for fields to be used when editing users in the admin page,
    # add_fieldsets is used for fields to be used when creating a user in the admin page.

    ordering = ('username', )

    list_display = ('username', 'email')

    fieldsets = (
            (
                # Fieldset name
                'Built-in',
                # Fieldset options
                {
                    'fields': (
                        'username',
                        'email',
                        'last_login',
                        'is_active',
                        'is_staff',
                        'is_superuser',
                        'date_joined'
                    ),
                    'classes': ('wide', 'extrapretty')
                }
            ),
            (
                'Duration and ratio',
                {
                    'fields': ('total_work_time', 'total_study_time', 'total_usable_time', 'time_usage_ratio'),
                    'classes': ('wide', 'extrapretty')
                }
            ),
            (
                'Object count',
                {
                    'fields': ('stage_count', 'day_count', 'session_count', 'subject_count'),
                    'classes': ('wide', 'extrapretty')
                }
            ),
        )

    add_fieldsets = (
            (
                # Fieldset name
                None,
                # Fieldset options
                {
                    'classes': ('wide', 'extrapretty'),
                    'fields': (
                        'username',
                        'email',
                        'password1',
                        'password2',
                        'is_active',
                        'is_staff',
                        'is_superuser',
                    ),
                },
            ),
        )

    # Displayed but non-editable fields
    readonly_fields = (
        'last_login',
        'date_joined',
        'total_work_time',
        'total_study_time',
        'total_usable_time',
        'time_usage_ratio',
        'stage_count',
        'day_count',
        'session_count',
        'subject_count'
    )


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    readonly_fields = ('day_of_week', 'session_count', 'usable_time', 'study_time', 'time_usage_ratio')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    readonly_fields = ('duration', )


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    readonly_fields = ('total_usable_time', 'total_study_time', 'total_work_time', 'day_count', 'session_count')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    readonly_fields = ('total_study_time', 'session_count')
