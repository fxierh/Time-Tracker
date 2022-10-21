from datetime import date, time

from django.test import TestCase, SimpleTestCase

from ..forms import StageCreateUpdateForm, SubjectCreateUpdateForm, DayCreateUpdateForm, DurationSelector, \
    SessionCreateUpdateForm
from ..models import User, Stage, Subject, Day, Session


# TODO: test create/update without the optional fields filled


class TestDurationSelectorWidget(SimpleTestCase):
    """Test the custom DurationSelector widget. """

    def setUp(self):
        self.selector = DurationSelector()

    def test_value_from_datadict(self):
        """Test the value_from_datadict function. """

        self.assertEqual(
            self.selector.value_from_datadict(
                {'prefix_hour': '1', 'prefix_minute': '10'},
                {},
                'prefix'
            ),
            4200,
            'Wrong output'
        )

    def test_decompress(self):
        """Test the decompress function. """

        self.assertEqual(self.selector.decompress(7800), [2, 10], 'Wrong output')


class TestStageCreateUpdateForm(TestCase):
    """Test the StageCreateUpdateForm. """

    def setUp(self):
        self.user = User.objects.create(username='fx', email='123@gmail.com')
        self.stage = Stage.objects.create(name='Stage', user=self.user)

    def test_create(self):
        """Test create form. """

        # Note: the user field is passed from view to form in reality
        form = StageCreateUpdateForm(
            user=self.user,
            data={
                'name': 'Stage 2',
                'description': 'Stage description'
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        stage = form.save(commit=False)
        stage.user = self.user
        stage.save()

    def test_update(self):
        """Test create form. """

        new_user = User.objects.create(username='fx2', email='234@gmail.com')

        # Note: instance=self.stage <=> per-populate the form with the existing object self.stage
        form = StageCreateUpdateForm(
            instance=self.stage,
            user=new_user,
            data={
                'name': 'Stage 2',
                'description': 'Stage 2 description'
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        stage = form.save(commit=False)
        stage.user = self.user
        stage.save()

    def test_user_stage_uniqueness_validation(self):
        """Test the validation ensuring stage is unique for each user. """

        # Create new stage
        Stage.objects.create(name='Stage 2', user=self.user)

        # Update the old stage's name to be the same as the new stage (should fail)
        form = StageCreateUpdateForm(
            instance=self.stage,
            user=self.user,
            data={
                'name': 'Stage 2'
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

        # Create a new stage whose name is the same as an existing stage (should fail)
        form = StageCreateUpdateForm(
            user=self.user,
            data={
                'name': 'Stage 2'
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')


class TestSubjectCreateUpdateForm(TestCase):
    """Test the SubjectCreateUpdateForm. """

    def setUp(self):
        self.user = User.objects.create(username='fx', email='123@gmail.com')
        self.subject = Subject.objects.create(name='Subject', user=self.user)

    def test_create(self):
        """Test create form. """

        form = SubjectCreateUpdateForm(
            user=self.user,
            data={
                'name': 'Subject 2',
                'description': 'Subject description'
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        subject = form.save(commit=False)
        subject.user = self.user
        subject.save()

    def test_update(self):
        """Test update form. """

        new_user = User.objects.create(username='fx2', email='234@gmail.com')

        form = SubjectCreateUpdateForm(
            instance=self.subject,
            user=new_user,
            data={
                'name': 'Subject 2',
                'description': 'Subject 2 description'
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        subject = form.save(commit=False)
        subject.user = self.user
        subject.save()

    def test_user_subject_uniqueness_validation(self):
        """Test the validation ensuring subject is unique for each user. """

        # Create new subject
        Subject.objects.create(name='Subject 2', user=self.user)

        # Update the old subject's name to be the same as the new subject (should fail)
        form = SubjectCreateUpdateForm(
            instance=self.subject,
            user=self.user,
            data={
                'name': 'Subject 2'
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

        # Create a new subject whose name is the same as an existing subject (should fail)
        form = SubjectCreateUpdateForm(
            user=self.user,
            data={
                'name': 'Subject 2'
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')


class TestDayCreateUpdateForm(TestCase):
    """Test the DayCreateUpdateForm. """

    def setUp(self):
        self.user = User.objects.create(username='fx', email='123@gmail.com')
        self.stage = Stage.objects.create(name='Stage', user=self.user)
        self.day = Day.objects.create(
            day=date(2022, 5, 5),
            stage=self.stage,
            user=self.user,
            start=time(9, 10),
            end=time(0, 10),
            end_next_day=True
        )

    def test_create(self):
        """Test create form. """

        form = DayCreateUpdateForm(
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': self.stage,
                # worktime has 2 fields since a multi-widget is used
                'worktime_hour': 2,
                'worktime_minute': 0,
                'start': time(10, 10),
                'end': time(0, 10),
                'end_next_day': True,
                'comment': 'Day comment'
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        day = form.save(commit=False)
        day.user = self.user
        day.save()

    def test_update(self):
        """Test update form. """

        new_stage = Stage.objects.create(name='Stage 2', user=self.user)

        form = DayCreateUpdateForm(
            instance=self.day,
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': new_stage,
                'worktime_hour': 2,
                'worktime_minute': 0,
                'start': time(10, 10),
                'end': time(1, 10),
                'end_next_day': True,
                'comment': 'Day comment'
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        day = form.save(commit=False)
        day.user = self.user
        day.save()

    def test_user_day_uniqueness_validation(self):
        """Test the validation ensuring day is unique for each user. """

        # Create new day
        Day.objects.create(
            day=date(2022, 5, 6),
            stage=self.stage,
            user=self.user,
            start=time(9, 10),
            end=time(0, 10),
            end_next_day=True
        )

        # Update the old day's name to be the same as the new day (should fail)
        form = DayCreateUpdateForm(
            instance=self.day,
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': self.stage,
                'worktime_hour': 2,
                'worktime_minute': 0,
                'start': time(10, 10),
                'end': time(1, 10),
                'end_next_day': True,
                'comment': 'Day comment'
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

        # Create a new day whose name is the same as an existing day (should fail)
        form = DayCreateUpdateForm(
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': self.stage,
                'start': time(11, 10),
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

    def test_usable_time_non_negative_validation(self):
        """Test the validation ensuring usable time is non-negative. """

        # Create a new day whose usable time is negative (should fail)
        form = DayCreateUpdateForm(
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': self.stage,
                'worktime_hour': 1,
                'worktime_minute': 1,
                'start': time(11, 10),
                'end': time(12, 10),
                'end_next_day': False
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

        # Update an existing day s.t. its usable time becomes negative (should fail)
        form = DayCreateUpdateForm(
            instance=self.day,
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': self.stage,
                'worktime_hour': 1,
                'worktime_minute': 1,
                'start': time(11, 10),
                'end': time(12, 10),
                'end_next_day': False
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

    def test_non_optional_fields_unspecified(self):
        """Test the form is valid when the non-optional fields are not specified."""

        form = DayCreateUpdateForm(
            user=self.user,
            data={
                'day': date(2022, 5, 6),
                'stage': self.stage,
                'start': time(11, 10),
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        day = form.save(commit=False)
        day.user = self.user
        day.save()


class TestSessionCreateUpdateForm(TestCase):
    """Test the SessionCreateUpdate form. """

    def setUp(self):
        self.user = User.objects.create(username='fx', email='123@gmail.com')
        self.stage = Stage.objects.create(name='Stage', user=self.user)
        self.day = Day.objects.create(
            day=date(2022, 5, 5),
            stage=self.stage,
            user=self.user,
            start=time(9, 10),
            end=time(0, 10),
            end_next_day=True
        )
        self.subject = Subject.objects.create(name='Subject', user=self.user)
        self.session = Session.objects.create(user=self.user, day=self.day, subject=self.subject, start=time(10, 10))

    def test_create(self):
        """Test create form. """

        form = SessionCreateUpdateForm(
            user=self.user,
            data={
                'day': self.day,
                'subject': self.subject,
                'start': time(22, 10),
                'end': time(0, 10),
                'end_next_day': True,
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        session = form.save(commit=False)
        session.user = self.user
        session.save()

    def test_update(self):
        """Test update form. """

        new_day = Day.objects.create(
            day=date(2022, 5, 6),
            stage=self.stage,
            user=self.user,
            start=time(9, 10),
            end=time(0, 10),
            end_next_day=True
        )
        new_subject = Subject.objects.create(name='Subject 2', user=self.user)

        form = SessionCreateUpdateForm(
            instance=self.session,
            user=self.user,
            data={
                'day': new_day,
                'subject': new_subject,
                'start': time(21, 10),
                'end': time(23, 10),
                'end_next_day': False,
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        session = form.save(commit=False)
        session.user = self.user
        session.save()

    def test_duration_positive_validation(self):
        """Test the validation ensuring session duration is positive. """

        # Create a new session with negative duration (should fail)
        form = SessionCreateUpdateForm(
            user=self.user,
            data={
                'day': self.day,
                'subject': self.subject,
                'start': time(22, 10),
                'end': time(22, 9),
                'end_next_day': False,
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

        # Update an existing session s.t. its duration becomes negative (should fail)
        form = SessionCreateUpdateForm(
            instance=self.session,
            user=self.user,
            data={
                'day': self.day,
                'subject': self.subject,
                'start': time(22, 10),
                'end': time(22, 9),
                'end_next_day': False,
            }
        )
        self.assertFalse(form.is_valid(), 'This form should not be valid')

    def test_non_optional_fields_unspecified(self):
        """Test the form is valid when the non-optional fields are not specified."""

        form = SessionCreateUpdateForm(
            user=self.user,
            data={
                'day': self.day,
                'subject': self.subject,
                'start': time(22, 10),
            }
        )
        self.assertTrue(form.is_valid(), 'This form should be valid')
        session = form.save(commit=False)
        session.user = self.user
        session.save()
