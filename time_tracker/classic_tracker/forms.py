from datetime import date

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import ModelForm, NumberInput, TimeInput, \
    TextInput, Textarea, DateInput, MultiWidget, Select, NullBooleanSelect
from django.utils import dateformat, timezone

from .models import Day, Session, Stage, Subject, time_diff_in_seconds


class TimeSelector(TimeInput):
    """Customized time selector widget"""

    # HTML input type, i.e. <input type="time">
    input_type = 'time'


class DateSelector(DateInput):
    """Customized date selector widget"""

    # HTML input type, i.e. <input type="date">
    input_type = 'date'


class DurationSelector(MultiWidget):
    """
    Customized duration selector composing of
    an hour selector (integer selector) and a minute selector (integer selector).
    """

    def __init__(
            self,
            min_hour: int = 0,
            max_hour: int = 24,
            step_hour: int = 1,
            min_minute: int = 0,
            max_minute: int = 59,
            step_minute: int = 1,
    ):
        # Syntax: widgets = {
        #   'field_name_suffix': widget,
        #   ...
        # }
        widgets = {
            'hour': NumberInput(attrs={
                'min': min_hour,
                'max': max_hour,
                'step': step_hour,
                'placeholder': 'hh',
                'class': 'col form-control'
            }),
            'minute': NumberInput(attrs={
                'min': min_minute,
                'max': max_minute,
                'step': step_minute,
                'placeholder': 'mm',
                'class': 'col form-control'
            }),
        }
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            hour, second = divmod(value, 3600)
            minute = second // 60
            return [hour, minute]

        return [None, None]  # pragma: no cover

    def value_from_datadict(self, data, files, name):
        hour, minute = super().value_from_datadict(data, files, name)
        hour = int(hour) if hour else 0
        minute = int(minute) if minute else 0

        return hour * 3600 + minute * 60


class DayCreateUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):

        # Get current user from view
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Make sure user only sees his own stages
        self.fields['stage'].queryset = Stage.objects.filter(user=self.user)

        # Set the default date and start time here so that they are updated upon page refresh
        self.fields['day'].initial = dateformat.format(timezone.now(), 'Y-m-d')
        self.fields['start'].initial = dateformat.format(timezone.now(), 'H:i')

    def clean(self):

        # Get cleaned data
        cleaned_data = super().clean()
        end_next_day = cleaned_data.get('end_next_day')
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        worktime = cleaned_data.get('worktime')
        day = cleaned_data.get('day')

        # Validation ensuring day is unique for each user
        if 'day' in self.changed_data and Day.objects.filter(Q(user=self.user) & Q(day=day)).exists():
            raise ValidationError("This day already exists !")

        # Validation ensuring usable time >= 0
        if start is not None and end is not None and end_next_day is not None and worktime is not None:
            usable_time = time_diff_in_seconds(start, end, end_next_day) - worktime

            if usable_time < 0:
                raise ValidationError("Usable time (end time - start time - worktime) must be non negative !")

    class Meta:

        model = Day
        fields = ['day', 'stage', 'worktime', 'start', 'end', 'end_next_day', 'comment']

        # Customize label to display for attribute
        labels = {
            'day': 'Date',
            'worktime': 'Worktime',
            'start': 'Start time',
            'end': 'End time',
            'end_next_day': 'Spans across midnight',
        }

        # Error message for attribute
        error_messages = {
            'worktime': {
                'min_value': 'Worktime should be non negative',
            },
        }

        # Customize widget for attribute.
        # Note: attrs = attributes to put in the corresponding html tag
        current_year = date.today().year
        widgets = {
            'day': DateSelector(attrs={'class': 'form-control'}),
            'stage': Select(attrs={'class': 'form-select'}),
            'worktime': DurationSelector,
            'start': TimeSelector(attrs={'class': 'form-control'}),
            'end': TimeSelector(attrs={'class': 'form-control'}),
            'end_next_day': NullBooleanSelect(attrs={'class': 'form-select'}),
            'comment': Textarea(attrs={
                'wrap': 'soft',
                'class': 'form-control',
                'rows': 5
            })
        }


class SessionCreateUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):

        # Get current user from view
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Make sure user only sees his own days and subjects
        self.fields['day'].queryset = Day.objects.filter(user=self.user).order_by('-day')
        self.fields['subject'].queryset = Subject.objects.filter(user=self.user)

        # Set the default date and start time here so that they are updated upon page refresh
        self.fields['start'].initial = dateformat.format(timezone.now(), 'H:i')

    def clean(self):

        # Get cleaned data
        cleaned_data = super().clean()
        end_next_day = cleaned_data.get('end_next_day')
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        # Validation ensuring duration > 0
        if start is not None and end is not None and end_next_day is not None:
            duration = time_diff_in_seconds(start, end, end_next_day)

            if duration <= 0:
                raise ValidationError("Duration (end time - start time) must be positive !")

    class Meta:

        model = Session
        fields = ['day', 'subject', 'start', 'end', 'end_next_day']

        # Customize label to display for attribute
        labels = {
            'day': 'Date',
            'subject': 'Subject',
            'start': 'Start time',
            'end': 'End time',
            'end_next_day': 'Spans across midnight',
        }

        # Customize widget for attribute
        widgets = {
            'day': Select(attrs={'class': 'form-select'}),
            'subject': Select(attrs={'class': 'form-select'}),
            'start': TimeSelector(attrs={'class': 'form-control'}),
            'end': TimeSelector(attrs={'class': 'form-control'}),
            'end_next_day': NullBooleanSelect(attrs={'class': 'form-select'}),
        }


class StageCreateUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        # Get current user from view
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        # Validation ensuring stage is unique for each user
        if 'name' in self.changed_data and Stage.objects.filter(Q(user=self.user) & Q(name=name)).exists():
            raise ValidationError("This stage already exists !")

    class Meta:
        model = Stage
        fields = ['name', 'description']

        # Customize label to display for attribute
        labels = {
            'name': 'Name',
            'description': 'Description'
        }

        # Customize widget for attribute
        widgets = {
            'name': TextInput(attrs={
                'placeholder': 'Ex. 2022Q1',
                'class': 'form-control',
                'size': 20,
            }),
            'description': Textarea(attrs={
                'wrap': 'soft',
                'placeholder': 'Ex. 1st quarter of 2022',
                'class': 'form-control',
                'rows': 5
            })
        }


class SubjectCreateUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        # Get current user from view
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        # Validation ensuring subject is unique for each user
        if 'name' in self.changed_data and Subject.objects.filter(Q(user=self.user) & Q(name=name)).exists():
            raise ValidationError("This subject already exists !")

    class Meta:
        model = Subject
        fields = ['name', 'description']

        # Customize label to display for attribute
        labels = {
            'name': 'Name',
            'description': 'Description'
        }

        # Customize widget for attribute
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'size': 20,
                'placeholder': 'Ex. CS',
            }),
            'description': Textarea(attrs={
                'wrap': 'soft',
                'placeholder': 'Ex. Computer Science',
                'class': 'form-control',
                'rows': 5
            })
        }
