from datetime import time, date, timedelta
from decimal import Decimal, ROUND_HALF_EVEN

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase, SimpleTestCase

from ..models import time_diff_in_seconds, Stage, User, Subject, Day, Session


class TestTimeDiffInSeconds(SimpleTestCase):
    """Test the time_diff_in_seconds function. """

    def test_end_time_before_midnight(self):
        """Test the case when end time is before midnight. """

        start = time(hour=11, minute=11)
        end = time(hour=13, minute=10)
        self.assertEqual(time_diff_in_seconds(start, end, False), 7140, f'Wrong duration')

    def test_end_time_after_midnight(self):
        """Test the case when end time is at or beyond midnight. """

        start = time(hour=23, minute=50)
        end = time(hour=1, minute=49)
        self.assertEqual(time_diff_in_seconds(start, end, True), 7140, f'Wrong duration')


class TestUser(TestCase):
    """Test the customized user model itself. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password = 'abcdefg'
        cls.is_superuser = False
        cls.username = 'fx'
        cls.first_name = 'f'
        cls.last_name = 'x'
        cls.email = '123@gmail.com'
        cls.is_staff = False
        cls.is_active = False
        cls.total_usable_time = 21600
        cls.total_study_time = 3600
        cls.total_work_time = 7200
        cls.stage_count = 2
        cls.day_count = 4
        cls.session_count = 8
        cls.subject_count = 2
        cls.time_usage_ratio = Decimal(cls.total_study_time / cls.total_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

    def test_create_user(self):
        """Test the case when a user is created. """

        User.objects.create(
            password=TestUser.password,
            is_superuser=TestUser.is_superuser,
            username=TestUser.username,
            first_name=TestUser.first_name,
            last_name=TestUser.last_name,
            email=TestUser.email,
            is_staff=TestUser.is_staff,
            is_active=TestUser.is_active,
            total_usable_time=TestUser.total_usable_time,
            total_study_time=TestUser.total_study_time,
            total_work_time=TestUser.total_work_time,
            stage_count=TestUser.stage_count,
            day_count=TestUser.day_count,
            session_count=TestUser.session_count,
            subject_count=TestUser.subject_count,
        )
        user_obj = User.objects.get(username=TestUser.username)

        # Check user
        self.assertEqual(user_obj.password, TestUser.password, 'Wrong password')
        self.assertEqual(user_obj.is_superuser, TestUser.is_superuser, 'Wrong is superuser')
        self.assertEqual(user_obj.username, TestUser.username, 'Wrong username')
        self.assertEqual(user_obj.first_name, TestUser.first_name, 'Wrong first name')
        self.assertEqual(user_obj.last_name, TestUser.last_name, 'Wrong last name')
        self.assertEqual(user_obj.email, TestUser.email, 'Wrong email')
        self.assertEqual(user_obj.is_staff, TestUser.is_staff, 'Wrong is staff')
        self.assertEqual(user_obj.is_active, TestUser.is_active, 'Wrong is active')
        self.assertEqual(user_obj.total_usable_time, TestUser.total_usable_time, 'Wrong total usable time')
        self.assertEqual(user_obj.total_study_time, TestUser.total_study_time, 'Wrong total study time')
        self.assertEqual(user_obj.total_work_time, TestUser.total_work_time, 'Wrong total work time')
        self.assertEqual(user_obj.stage_count, TestUser.stage_count, 'Wrong stage count')
        self.assertEqual(user_obj.day_count, TestUser.day_count, 'Wrong day count')
        self.assertEqual(user_obj.session_count, TestUser.session_count, 'Wrong session count')
        self.assertEqual(user_obj.subject_count, TestUser.subject_count, 'Wrong subject count')
        self.assertEqual(user_obj.time_usage_ratio, TestUser.time_usage_ratio, 'Wrong time usage ratio')

    def test_update_user(self):
        """Test the case when a user is updated. """

        User.objects.create(
            password=TestUser.password,
            is_superuser=TestUser.is_superuser,
            username=TestUser.username,
            first_name=TestUser.first_name,
            last_name=TestUser.last_name,
            email=TestUser.email,
            is_staff=TestUser.is_staff,
            is_active=TestUser.is_active,
            total_usable_time=TestUser.total_usable_time,
            total_study_time=TestUser.total_study_time,
            total_work_time=TestUser.total_work_time,
            stage_count=TestUser.stage_count,
            day_count=TestUser.day_count,
            session_count=TestUser.session_count,
            subject_count=TestUser.subject_count,
        )

        new_password = 'abcde'
        new_is_superuser = True
        new_username = 'fx2'
        new_first_name = 'f2'
        new_last_name = 'x2'
        new_email = '1234@gmail.com'
        new_is_staff = True
        new_is_active = True
        new_total_usable_time = 36000
        new_total_study_time = 7200
        new_total_work_time = 10800
        new_stage_count = 3
        new_day_count = 6
        new_session_count = 12
        new_subject_count = 6
        new_time_usage_ratio = Decimal(new_total_study_time / new_total_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

        user_obj = User.objects.get(username=TestUser.username)
        user_obj.password = new_password
        user_obj.is_superuser = new_is_superuser
        user_obj.username = new_username
        user_obj.first_name = new_first_name
        user_obj.last_name = new_last_name
        user_obj.email = new_email
        user_obj.is_staff = new_is_staff
        user_obj.is_active = new_is_active
        user_obj.total_usable_time = new_total_usable_time
        user_obj.total_study_time = new_total_study_time
        user_obj.total_work_time = new_total_work_time
        user_obj.stage_count = new_stage_count
        user_obj.day_count = new_day_count
        user_obj.session_count = new_session_count
        user_obj.subject_count = new_subject_count
        user_obj.save()
        user_obj = User.objects.get(username=new_username)

        # Check user
        self.assertEqual(user_obj.password, new_password, 'Wrong password')
        self.assertEqual(user_obj.is_superuser, new_is_superuser, 'Wrong is superuser')
        self.assertEqual(user_obj.username, new_username, 'Wrong username')
        self.assertEqual(user_obj.first_name, new_first_name, 'Wrong first name')
        self.assertEqual(user_obj.last_name, new_last_name, 'Wrong last name')
        self.assertEqual(user_obj.email, new_email, 'Wrong email')
        self.assertEqual(user_obj.is_staff, new_is_staff, 'Wrong is staff')
        self.assertEqual(user_obj.is_active, new_is_active, 'Wrong is active')
        self.assertEqual(user_obj.total_usable_time, new_total_usable_time, 'Wrong total usable time')
        self.assertEqual(user_obj.total_study_time, new_total_study_time, 'Wrong total study time')
        self.assertEqual(user_obj.total_work_time, new_total_work_time, 'Wrong total work time')
        self.assertEqual(user_obj.stage_count, new_stage_count, 'Wrong stage count')
        self.assertEqual(user_obj.day_count, new_day_count, 'Wrong day count')
        self.assertEqual(user_obj.session_count, new_session_count, 'Wrong session count')
        self.assertEqual(user_obj.subject_count, new_subject_count, 'Wrong subject count')
        self.assertEqual(user_obj.time_usage_ratio, new_time_usage_ratio, 'Wrong time usage ratio')

    def test_delete_user(self):
        """Test the case when a user is deleted. """

        User.objects.create(
            password=TestUser.password,
            is_superuser=TestUser.is_superuser,
            username=TestUser.username,
            first_name=TestUser.first_name,
            last_name=TestUser.last_name,
            email=TestUser.email,
            is_staff=TestUser.is_staff,
            is_active=TestUser.is_active,
            total_usable_time=TestUser.total_usable_time,
            total_study_time=TestUser.total_study_time,
            total_work_time=TestUser.total_work_time,
            stage_count=TestUser.stage_count,
            day_count=TestUser.day_count,
            session_count=TestUser.session_count,
            subject_count=TestUser.subject_count,
        )
        user_obj = User.objects.get(username=TestUser.username)
        user_obj.delete()

        # Check user
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            User.objects.get(username=TestUser.username)


class TestStage(TestCase):
    """Test the stage model and its interaction with its upstream, the user model. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.name = 'Stage'
        cls.username = 'fx'
        User.objects.create(username=cls.username, email='123@gmail.com')
        cls.description = 'Stage description'
        cls.day_count = 200
        cls.session_count = 300
        cls.total_usable_time = 30000
        cls.total_study_time = 15000
        cls.total_work_time = 10000
        cls.time_usage_ratio = cls.total_study_time / cls.total_usable_time

    def test_create_stage(self):
        """Test the case when a stage is created. """

        Stage.objects.create(
            name=TestStage.name,
            user=User.objects.get(username=TestStage.username),
            description=TestStage.description,
            day_count=TestStage.day_count,
            session_count=TestStage.session_count,
            total_usable_time=TestStage.total_usable_time,
            total_study_time=TestStage.total_study_time,
            total_work_time=TestStage.total_work_time,
        )
        stage_obj = Stage.objects.get(name=TestStage.name)

        # Check stage
        # TODO: understand why the name and description fields are case sensitive
        #  even though the column collations are case insensitive
        self.assertEqual(stage_obj.name, TestStage.name, 'Wrong name')
        self.assertEqual(stage_obj.description, TestStage.description, 'Wrong description')
        self.assertEqual(stage_obj.day_count, TestStage.day_count, 'Wrong day count')
        self.assertEqual(stage_obj.session_count, TestStage.session_count, 'Wrong session count')
        self.assertEqual(stage_obj.total_study_time, TestStage.total_study_time, 'Wrong total study time')
        self.assertEqual(stage_obj.total_usable_time, TestStage.total_usable_time, 'Wrong total usable time')
        self.assertEqual(stage_obj.total_work_time, TestStage.total_work_time, 'Wrong total work time')
        self.assertEqual(stage_obj.time_usage_ratio, TestStage.time_usage_ratio, 'Wrong time usage ratio')

        # Check associated user
        self.assertEqual(stage_obj.user.stage_count, 1, 'Wrong stage count of associated user')
        self.assertEqual(stage_obj.user.day_count, TestStage.day_count, 'Wrong day count of associated user')
        self.assertEqual(
            stage_obj.user.session_count,
            TestStage.session_count,
            'Wrong session count of associated user'
        )
        self.assertEqual(stage_obj.user.subject_count, 0, 'Wrong subject count of associated user')
        self.assertEqual(
            stage_obj.user.total_usable_time,
            TestStage.total_usable_time,
            'Wrong total usable time of associated user'
        )
        self.assertEqual(
            stage_obj.user.total_study_time,
            TestStage.total_study_time,
            'Wrong total study time of associated user'
        )
        self.assertEqual(
            stage_obj.user.total_work_time,
            TestStage.total_work_time,
            'Wrong total work time of associated user'
        )
        self.assertEqual(stage_obj.user.time_usage_ratio,
             TestStage.time_usage_ratio,
             'Wrong time usage ratio of associated user'
         )

    def test_update_stage(self):
        """Test the case when a stage is updated. """

        Stage.objects.create(
            name=TestStage.name,
            user=User.objects.get(username=TestStage.username),
            description=TestStage.description,
            day_count=TestStage.day_count,
            session_count=TestStage.session_count,
            total_usable_time=TestStage.total_usable_time,
            total_study_time=TestStage.total_study_time,
            total_work_time=TestStage.total_work_time,
        )
        new_name = 'Stage 1'
        new_description = 'Stage 1 description'
        new_day_count = 201
        new_session_count = 301
        new_total_usable_time = 30002
        new_total_study_time = 15001
        new_total_work_time = 10001
        new_time_usage_ratio = new_total_study_time / new_total_usable_time

        stage_obj = Stage.objects.get(name=TestStage.name)
        stage_obj.name = new_name
        stage_obj.description = new_description
        stage_obj.day_count = new_day_count
        stage_obj.session_count = new_session_count
        stage_obj.total_usable_time = new_total_usable_time
        stage_obj.total_study_time = new_total_study_time
        stage_obj.total_work_time = new_total_work_time
        stage_obj.save()
        stage_obj = Stage.objects.get(name=new_name)

        # Check stage
        self.assertEqual(stage_obj.name, new_name, 'Wrong name')
        self.assertEqual(stage_obj.description, new_description, 'Wrong description')
        self.assertEqual(stage_obj.day_count, new_day_count, 'Wrong day count')
        self.assertEqual(stage_obj.session_count, new_session_count, 'Wrong session count')
        self.assertEqual(stage_obj.total_study_time, new_total_study_time, 'Wrong total study time')
        self.assertEqual(stage_obj.total_usable_time, new_total_usable_time, 'Wrong total usable time')
        self.assertEqual(stage_obj.total_work_time, new_total_work_time, 'Wrong total work time')
        self.assertEqual(stage_obj.time_usage_ratio, new_time_usage_ratio, 'Wrong time usage ratio')

        # Check associated user
        self.assertEqual(stage_obj.user.stage_count, 1, 'Wrong stage count of associated user')
        self.assertEqual(stage_obj.user.day_count, new_day_count, 'Wrong day count of associated user')
        self.assertEqual(stage_obj.user.session_count, new_session_count, 'Wrong session count of associated user')
        self.assertEqual(stage_obj.user.subject_count, 0, 'Wrong subject count of associated user')
        self.assertEqual(
            stage_obj.user.total_usable_time,
            new_total_usable_time,
            'Wrong total usable time of associated user'
        )
        self.assertEqual(
            stage_obj.user.total_study_time,
            new_total_study_time,
            'Wrong total study time of associated user'
        )
        self.assertEqual(
            stage_obj.user.total_work_time,
            new_total_work_time,
            'Wrong total work time of associated user'
        )
        self.assertEqual(
            stage_obj.user.time_usage_ratio,
            new_time_usage_ratio,
            'Wrong time usage ratio of associated user'
        )

    def test_delete_stage(self):
        """Test the case when a stage is removed. """

        Stage.objects.create(
            name=TestStage.name,
            user=User.objects.get(username=TestStage.username),
            description=TestStage.description,
            day_count=TestStage.day_count,
            session_count=TestStage.session_count,
            total_usable_time=TestStage.total_usable_time,
            total_study_time=TestStage.total_study_time,
            total_work_time=TestStage.total_work_time,
        )
        stage_obj = Stage.objects.get(name=TestStage.name)
        stage_obj.delete()

        # Check stage
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            Stage.objects.get(name=TestStage.name)

        # Check associated user
        self.assertEqual(stage_obj.user.stage_count, 0, 'Wrong stage count of associated user')
        self.assertEqual(stage_obj.user.day_count, 0, 'Wrong day count of associated user')
        self.assertEqual(stage_obj.user.session_count, 0, 'Wrong session count of associated user')
        self.assertEqual(stage_obj.user.subject_count, 0, 'Wrong subject count of associated user')
        self.assertEqual(stage_obj.user.total_usable_time, 0, 'Wrong total usable time of associated user')
        self.assertEqual(stage_obj.user.total_study_time, 0, 'Wrong total study time of associated user')
        self.assertEqual(stage_obj.user.total_work_time, 0, 'Wrong total work time of associated user')
        self.assertEqual(stage_obj.user.time_usage_ratio, 0, 'Wrong time usage ratio of associated user')

    def test_user_stage_uniqueness(self):
        """Test the database level constraint which ensures the uniqueness of the (user, stage) combination. """

        Stage.objects.create(
            name=TestStage.name,
            user=User.objects.get(username=TestStage.username),
            description=TestStage.description,
            day_count=TestStage.day_count,
            session_count=TestStage.session_count,
            total_usable_time=TestStage.total_usable_time,
            total_study_time=TestStage.total_study_time,
            total_work_time=TestStage.total_work_time,
        )

        with self.assertRaisesRegex(
            IntegrityError,
            '.*user_stage_uniqueness.*',
            msg='Wrong user stage uniqueness exception'
        ):
            Stage.objects.create(
                name=TestStage.name,
                user=User.objects.get(username=TestStage.username),
                description=TestStage.description,
                day_count=TestStage.day_count,
                session_count=TestStage.session_count,
                total_usable_time=TestStage.total_usable_time,
                total_study_time=TestStage.total_study_time,
                total_work_time=TestStage.total_work_time,
            )


class TestSubject(TestCase):
    """Test the subject model and its interaction with its upstream, the user model. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'fx'
        User.objects.create(username=cls.username, email='123@gmail.com')
        cls.name = 'Subject'
        cls.description = 'Subject description'
        cls.total_study_time = 10000
        cls.session_count = 100

    def test_create_subject(self):
        """Test the case when a subject is created. """

        Subject.objects.create(
            name=TestSubject.name,
            user=User.objects.get(username=TestSubject.username),
            description=TestSubject.description,
            total_study_time=TestSubject.total_study_time,
            session_count=TestSubject.session_count,
        )
        subject_obj = Subject.objects.get(name=TestSubject.name)

        # Check subject
        self.assertEqual(subject_obj.name, TestSubject.name, 'Wrong name')
        self.assertEqual(subject_obj.description, TestSubject.description, 'Wrong description')
        self.assertEqual(subject_obj.session_count, TestSubject.session_count, 'Wrong session count')
        self.assertEqual(subject_obj.total_study_time, TestSubject.total_study_time, 'Wrong total study time')

        # Check associated user
        self.assertEqual(subject_obj.user.stage_count, 0, 'Wrong stage count of associated user')
        self.assertEqual(subject_obj.user.day_count, 0, 'Wrong day count of associated user')
        self.assertEqual(subject_obj.user.session_count, 0, 'Wrong session count of associated user')
        self.assertEqual(subject_obj.user.subject_count, 1, 'Wrong subject count of associated user')
        self.assertEqual(subject_obj.user.total_usable_time, 0, 'Wrong total usable time of associated user')
        self.assertEqual(subject_obj.user.total_study_time, 0, 'Wrong total study time of associated user')
        self.assertEqual(subject_obj.user.total_work_time, 0, 'Wrong total work time of associated user')
        self.assertEqual(subject_obj.user.time_usage_ratio, 0, 'Wrong time usage ratio of associated user')

    def test_update_subject(self):
        """Test the case when a subject is updated. """

        Subject.objects.create(
            name=TestSubject.name,
            user=User.objects.get(username=TestSubject.username),
            description=TestSubject.description,
            total_study_time=TestSubject.total_study_time,
            session_count=TestSubject.session_count,
        )
        new_name = 'Subject 1'
        new_description = 'Subject 1 description'
        new_total_study_time = 10001
        new_session_count = 101

        subject_obj = Subject.objects.get(name=TestSubject.name)
        subject_obj.name = new_name
        subject_obj.description = new_description
        subject_obj.total_study_time = new_total_study_time
        subject_obj.session_count = new_session_count
        subject_obj.save()
        subject_obj = Subject.objects.get(name=new_name)

        # Check subject
        self.assertEqual(subject_obj.name, new_name, 'Wrong name')
        self.assertEqual(subject_obj.description, new_description, 'Wrong description')
        self.assertEqual(subject_obj.session_count, new_session_count, 'Wrong session count')
        self.assertEqual(subject_obj.total_study_time, new_total_study_time, 'Wrong total study time')

        # Check associated user
        self.assertEqual(subject_obj.user.stage_count, 0, 'Wrong stage count of associated user')
        self.assertEqual(subject_obj.user.day_count, 0, 'Wrong day count of associated user')
        self.assertEqual(subject_obj.user.session_count, 0, 'Wrong session count of associated user')
        self.assertEqual(subject_obj.user.subject_count, 1, 'Wrong subject count of associated user')
        self.assertEqual(subject_obj.user.total_usable_time, 0, 'Wrong total usable time of associated user')
        self.assertEqual(subject_obj.user.total_study_time, 0, 'Wrong total study time of associated user')
        self.assertEqual(subject_obj.user.total_work_time, 0, 'Wrong total work time of associated user')
        self.assertEqual(subject_obj.user.time_usage_ratio, 0, 'Wrong time usage ratio of associated user')

    def test_delete_subject(self):
        """Test the case when a subject is removed. """

        Subject.objects.create(
            name=TestSubject.name,
            user=User.objects.get(username=TestSubject.username),
            description=TestSubject.description,
            total_study_time=TestSubject.total_study_time,
            session_count=TestSubject.session_count,
        )
        subject_obj = Subject.objects.get(name=TestSubject.name)
        subject_obj.delete()

        # Check subject
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            Subject.objects.get(name=TestSubject.name)

        # Check associated user
        self.assertEqual(subject_obj.user.stage_count, 0, 'Wrong stage count of associated user')
        self.assertEqual(subject_obj.user.day_count, 0, 'Wrong day count of associated user')
        self.assertEqual(subject_obj.user.session_count, 0, 'Wrong session count of associated user')
        self.assertEqual(subject_obj.user.subject_count, 0, 'Wrong subject count of associated user')
        self.assertEqual(subject_obj.user.total_usable_time, 0, 'Wrong total usable time of associated user')
        self.assertEqual(subject_obj.user.total_study_time, 0, 'Wrong total study time of associated user')
        self.assertEqual(subject_obj.user.total_work_time, 0, 'Wrong total work time of associated user')
        self.assertEqual(subject_obj.user.time_usage_ratio, 0, 'Wrong time usage ratio of associated user')

    def test_user_subject_uniqueness(self):
        """Test the database level constraint which ensures the uniqueness of the (user, subject) combination."""

        Subject.objects.create(
            name=TestSubject.name,
            user=User.objects.get(username=TestSubject.username),
            description=TestSubject.description,
            total_study_time=TestSubject.total_study_time,
            session_count=TestSubject.session_count,
        )

        with self.assertRaisesRegex(
                IntegrityError,
                '.*user_subject_uniqueness.*',
                msg='Wrong user subject uniqueness exception'
        ):
            Subject.objects.create(
                name=TestSubject.name,
                user=User.objects.get(username=TestSubject.username),
                description=TestSubject.description,
                total_study_time=TestSubject.total_study_time,
                session_count=TestSubject.session_count,
            )


class TestDay(TestCase):
    """Test the day model and its interaction with its upstream, the stage model. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_obj = User.objects.create(username='fx', email='123@gmail.com')
        Stage.objects.create(name='Stage', user=user_obj, description='Stage description')
        cls.day = date(year=2022, month=5, day=6)
        cls.session_count = 10
        cls.worktime = 9000
        cls.start = time(hour=9, minute=10)
        cls.end = time(hour=19, minute=10)
        cls.end_next_day = False
        cls.study_time = 18000
        cls.usable_time = time_diff_in_seconds(cls.start, cls.end, cls.end_next_day) - cls.worktime
        # Round to 4 decimal places, using the same method as the Python built-in Round function
        cls.time_usage_ratio = Decimal(cls.study_time / cls.usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)
        cls.comment = 'Day comment'

    def test_day_create_with_end_time(self):
        """Test the case when a day with end time specified is created. """

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            end=TestDay.end,
            end_next_day=TestDay.end_next_day,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )
        day_obj = Day.objects.get(day=TestDay.day)

        # Check day
        self.assertEqual(day_obj.day, TestDay.day, 'Wrong date')
        self.assertEqual(day_obj.day_of_week, TestDay.day.isoweekday(), 'Wrong day of week')
        self.assertEqual(day_obj.session_count, TestDay.session_count, 'Wrong session count')
        self.assertEqual(day_obj.worktime, TestDay.worktime, 'Wrong worktime')
        self.assertEqual(day_obj.start, TestDay.start, 'Wrong start time')
        self.assertEqual(day_obj.end, TestDay.end, 'Wrong end time')
        self.assertEqual(day_obj.end_next_day, TestDay.end_next_day, 'Wrong end next day')
        self.assertEqual(day_obj.usable_time, TestDay.usable_time, 'Wrong usable time')
        self.assertEqual(day_obj.study_time, TestDay.study_time, 'Wrong study time')
        self.assertEqual(
            day_obj.time_usage_ratio,
            TestDay.time_usage_ratio,
            'Wrong time usage ratio'
        )
        self.assertEqual(day_obj.comment, TestDay.comment, 'Wrong comment')

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 1, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, TestDay.session_count, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            TestDay.usable_time,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            TestDay.worktime,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            TestDay.study_time,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            TestDay.time_usage_ratio,
            'Wrong time usage ratio of associated stage'
        )

    def test_day_create_no_end_time(self):
        """Test the case when end time and end next day are not specified. """

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )
        day_obj = Day.objects.get(day=TestDay.day)

        # Check day
        self.assertEqual(day_obj.day, TestDay.day, 'Wrong date')
        self.assertEqual(day_obj.day_of_week, TestDay.day.isoweekday(), 'Wrong day of week')
        self.assertEqual(day_obj.session_count, TestDay.session_count, 'Wrong session count')
        self.assertEqual(day_obj.worktime, TestDay.worktime, 'Wrong worktime')
        self.assertEqual(day_obj.start, TestDay.start, 'Wrong start time')
        self.assertEqual(day_obj.end, None, 'Wrong end time')
        self.assertEqual(day_obj.end_next_day, False, 'Wrong end next day')
        self.assertEqual(day_obj.usable_time, 0, 'Wrong usable time')
        self.assertEqual(day_obj.study_time, TestDay.study_time, 'Wrong study time')
        self.assertEqual(day_obj.time_usage_ratio, 0, 'Wrong time usage ratio')
        self.assertEqual(day_obj.comment, TestDay.comment, 'Wrong comment')

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 1, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, TestDay.session_count, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            0,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            TestDay.worktime,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            TestDay.study_time,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            0,
            'Wrong time usage ratio of associated stage'
        )

    def test_day_create_end_next_day(self):
        """Test the case when a day ends after (i.e. >=) midnight. """

        end = time(hour=0, minute=10)
        end_next_day = True
        usable_time = time_diff_in_seconds(TestDay.start, end, end_next_day) - TestDay.worktime
        time_usage_ratio = Decimal(TestDay.study_time / usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            end=end,
            end_next_day=end_next_day,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )
        day_obj = Day.objects.get(day=TestDay.day)

        # Check day
        self.assertEqual(day_obj.day, TestDay.day, 'Wrong date')
        self.assertEqual(day_obj.day_of_week, TestDay.day.isoweekday(), 'Wrong day of week')
        self.assertEqual(day_obj.session_count, TestDay.session_count, 'Wrong session count')
        self.assertEqual(day_obj.worktime, TestDay.worktime, 'Wrong worktime')
        self.assertEqual(day_obj.start, TestDay.start, 'Wrong start time')
        self.assertEqual(day_obj.end, end, 'Wrong end time')
        self.assertEqual(day_obj.end_next_day, end_next_day, 'Wrong end next day')
        self.assertEqual(day_obj.usable_time, usable_time, 'Wrong usable time')
        self.assertEqual(day_obj.study_time, TestDay.study_time, 'Wrong study time')
        self.assertEqual(
            day_obj.time_usage_ratio,
            time_usage_ratio,
            'Wrong time usage ratio'
        )
        self.assertEqual(day_obj.comment, TestDay.comment, 'Wrong comment')

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 1, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, TestDay.session_count, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            usable_time,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            TestDay.worktime,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            TestDay.study_time,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            time_usage_ratio,
            'Wrong time usage ratio of associated stage'
        )

    def test_day_update_change_end_time(self):
        """Test the case when end time and end next day were specified and are now changed. """

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            end=TestDay.end,
            end_next_day=TestDay.end_next_day,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )

        new_stage = Stage.objects.create(
            name='Stage 2',
            user=User.objects.get(username='fx'),
            description='Stage 2 description'
        )
        new_day = date(year=2022, month=5, day=7)
        new_session_count = 8
        new_worktime = 12600
        new_start = time(hour=10, minute=10)
        new_end = time(hour=00, minute=10)
        new_end_next_day = True
        new_study_time = 21600
        new_usable_time = time_diff_in_seconds(new_start, new_end, new_end_next_day) - new_worktime
        new_time_usage_ratio = Decimal(new_study_time / new_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)
        new_comment = 'Day comment 1'

        day_obj = Day.objects.get(day=TestDay.day)
        day_obj.stage = new_stage
        day_obj.day = new_day
        day_obj.session_count = new_session_count
        day_obj.worktime = new_worktime
        day_obj.start = new_start
        day_obj.end = new_end
        day_obj.end_next_day = new_end_next_day
        day_obj.study_time = new_study_time
        day_obj.comment = new_comment
        day_obj.save()
        day_obj = Day.objects.get(day=new_day)

        # Check day
        self.assertEqual(day_obj.stage, new_stage, 'Wrong stage')
        self.assertEqual(day_obj.day, new_day, 'Wrong date')
        self.assertEqual(day_obj.day_of_week, new_day.isoweekday(), 'Wrong day of week')
        self.assertEqual(day_obj.session_count, new_session_count, 'Wrong session count')
        self.assertEqual(day_obj.worktime, new_worktime, 'Wrong worktime')
        self.assertEqual(day_obj.start, new_start, 'Wrong start time')
        self.assertEqual(day_obj.end, new_end, 'Wrong end time')
        self.assertEqual(day_obj.end_next_day, new_end_next_day, 'Wrong end next day')
        self.assertEqual(day_obj.usable_time, new_usable_time, 'Wrong usable time')
        self.assertEqual(day_obj.study_time, new_study_time, 'Wrong study time')
        self.assertEqual(
            day_obj.time_usage_ratio,
            new_time_usage_ratio,
            'Wrong time usage ratio'
        )
        self.assertEqual(day_obj.comment, new_comment, 'Wrong comment')

        # Check old stage
        old_stage = Stage.objects.get(name='Stage')
        self.assertEqual(old_stage.day_count, 0, 'Wrong day count of the previous associated stage')
        self.assertEqual(old_stage.session_count, 0, 'Wrong session count of the previous associated stage')
        self.assertEqual(
            old_stage.total_usable_time,
            0,
            'Wrong total usable time of the previous associated stage'
        )
        self.assertEqual(
            old_stage.total_work_time,
            0,
            'Wrong total work time of the previous associated stage'
        )
        self.assertEqual(
            old_stage.total_study_time,
            0,
            'Wrong total study time of the previous associated stage'
        )
        self.assertEqual(
            old_stage.time_usage_ratio,
            0,
            'Wrong time usage ratio of the previous associated stage'
        )

        # Check new stage
        self.assertEqual(day_obj.stage.day_count, 1, 'Wrong day count of the new associated stage')
        self.assertEqual(
            day_obj.stage.session_count,
            new_session_count,
            'Wrong session count of the new associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_usable_time,
            new_usable_time,
            'Wrong total usable time of the new associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            new_worktime,
            'Wrong total work time of the new associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            new_study_time,
            'Wrong total study time of the new associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            new_time_usage_ratio,
            'Wrong time usage ratio of the new associated stage'
        )

    def test_day_update_add_end_time(self):
        """Test the case when end time and end next day were not specified and are specified now. """

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )

        new_end = time(hour=00, minute=10)
        new_end_next_day = True
        new_usable_time = time_diff_in_seconds(TestDay.start, new_end, new_end_next_day) - TestDay.worktime
        new_time_usage_ratio = Decimal(TestDay.study_time / new_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

        day_obj = Day.objects.get(day=TestDay.day)
        day_obj.end = new_end
        day_obj.end_next_day = new_end_next_day
        day_obj.save()
        day_obj = Day.objects.get(day=TestDay.day)

        # Check day
        self.assertEqual(day_obj.day, TestDay.day, 'Wrong date')
        self.assertEqual(day_obj.day_of_week, TestDay.day.isoweekday(), 'Wrong day of week')
        self.assertEqual(day_obj.session_count, TestDay.session_count, 'Wrong session count')
        self.assertEqual(day_obj.worktime, TestDay.worktime, 'Wrong worktime')
        self.assertEqual(day_obj.start, TestDay.start, 'Wrong start time')
        self.assertEqual(day_obj.end, new_end, 'Wrong end time')
        self.assertEqual(day_obj.end_next_day, new_end_next_day, 'Wrong end next day')
        self.assertEqual(day_obj.usable_time, new_usable_time, 'Wrong usable time')
        self.assertEqual(day_obj.study_time, TestDay.study_time, 'Wrong study time')
        self.assertEqual(
            day_obj.time_usage_ratio,
            new_time_usage_ratio,
            'Wrong time usage ratio'
        )
        self.assertEqual(day_obj.comment, TestDay.comment, 'Wrong comment')

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 1, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, TestDay.session_count, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            new_usable_time,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            TestDay.worktime,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            TestDay.study_time,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            new_time_usage_ratio,
            'Wrong time usage ratio of associated stage'
        )

    def test_day_update_remove_end_time(self):
        """Test the case when end time and end next day were specified but are not removed. """

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            end=TestDay.end,
            end_next_day=TestDay.end_next_day,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )

        day_obj = Day.objects.get(day=TestDay.day)
        day_obj.end = None
        day_obj.end_next_day = None
        day_obj.save()
        day_obj = Day.objects.get(day=TestDay.day)

        # Check day
        self.assertEqual(day_obj.day, TestDay.day, 'Wrong date')
        self.assertEqual(day_obj.day_of_week, TestDay.day.isoweekday(), 'Wrong day of week')
        self.assertEqual(day_obj.session_count, TestDay.session_count, 'Wrong session count')
        self.assertEqual(day_obj.worktime, TestDay.worktime, 'Wrong worktime')
        self.assertEqual(day_obj.start, TestDay.start, 'Wrong start time')
        self.assertEqual(day_obj.end, None, 'Wrong end time')
        self.assertEqual(day_obj.end_next_day, None, 'Wrong end next day')
        self.assertEqual(day_obj.usable_time, 0, 'Wrong usable time')
        self.assertEqual(day_obj.study_time, TestDay.study_time, 'Wrong study time')
        self.assertEqual(day_obj.time_usage_ratio, 0, 'Wrong time usage ratio')
        self.assertEqual(day_obj.comment, TestDay.comment, 'Wrong comment')

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 1, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, TestDay.session_count, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            0,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            TestDay.worktime,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            TestDay.study_time,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            0,
            'Wrong time usage ratio of associated stage'
        )

    def test_day_delete_with_end_time(self):
        """Test the case when a day with end time specified is deleted."""

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            end=TestDay.end,
            end_next_day=TestDay.end_next_day,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )
        day_obj = Day.objects.get(day=TestDay.day)
        day_obj.delete()

        # Check day
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            Day.objects.get(day=TestDay.day)

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 0, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, 0, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            0,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            0,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            0,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            0,
            'Wrong time usage ratio of associated stage'
        )

    def test_day_delete_no_end_time(self):
        """Test the case when a day with no end time and no end next day is deleted. """

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )
        day_obj = Day.objects.get(day=TestDay.day)
        day_obj.delete()

        # Check day
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            Day.objects.get(day=TestDay.day)

        # Check stage
        self.assertEqual(day_obj.stage.day_count, 0, 'Wrong day count of associated stage')
        self.assertEqual(day_obj.stage.session_count, 0, 'Wrong session count of associated stage')
        self.assertEqual(
            day_obj.stage.total_usable_time,
            0,
            'Wrong total usable time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_work_time,
            0,
            'Wrong total work time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.total_study_time,
            0,
            'Wrong total study time of associated stage'
        )
        self.assertEqual(
            day_obj.stage.time_usage_ratio,
            0,
            'Wrong time usage ratio of associated stage'
        )

    def test_user_day_uniqueness(self):
        """Test the database level constraint which ensures the uniqueness of the (user, day) combination."""

        Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=TestDay.day,
            session_count=TestDay.session_count,
            worktime=TestDay.worktime,
            start=TestDay.start,
            end=TestDay.end,
            end_next_day=TestDay.end_next_day,
            study_time=TestDay.study_time,
            comment=TestDay.comment,
        )

        with self.assertRaisesRegex(
            IntegrityError,
            '.*user_day_uniqueness.*',
            msg='Wrong user day uniqueness exception'
        ):
            Day.objects.create(
                user=User.objects.get(username='fx'),
                stage=Stage.objects.get(name='Stage'),
                day=TestDay.day,
                session_count=TestDay.session_count,
                worktime=TestDay.worktime,
                start=TestDay.start,
                end=TestDay.end,
                end_next_day=TestDay.end_next_day,
                study_time=TestDay.study_time,
                comment=TestDay.comment,
            )

    def test_time_usage_ratio_range(self):
        """
        Test the database level constraint which restricts the time usage ratio
        to be between 0 and 1 (both ends inclusive).
        """

        with self.assertRaisesRegex(
            IntegrityError,
            '.*day_time_usage_ratio_range.*',
            msg='Wrong time usage ratio exception'
        ):
            Day.objects.create(
                user=User.objects.get(username='fx'),
                stage=Stage.objects.get(name='Stage'),
                day=TestDay.day,
                session_count=TestDay.session_count,
                worktime=TestDay.worktime,
                start=TestDay.start,
                end=TestDay.end,
                end_next_day=TestDay.end_next_day,
                study_time=TestDay.usable_time + 100,
                comment=TestDay.comment,
            )


class TestSession(TestCase):
    """Test the session model and its interaction with its upstreams, the day model and the subject model. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'fx'
        cls.day = date(2022, 5, 6)
        cls.day_of_week = cls.day.isoweekday()
        cls.day_worktime = 3600
        cls.day_start = time(14, 10)
        cls.day_end = time(2, 10)
        cls.day_end_next_day = True
        cls.day_usable_time = time_diff_in_seconds(cls.day_start, cls.day_end, cls.day_end_next_day) - cls.day_worktime
        user_obj = User.objects.create(username=TestSession.username, email='123@gmail.com')
        stage_obj = Stage.objects.create(name='Stage', user=user_obj, description='Stage description')
        Day.objects.create(
            user=user_obj,
            stage=stage_obj,
            day=TestSession.day,
            worktime=cls.day_worktime,
            start=cls.day_start,
            end=cls.day_end,
            end_next_day=cls.day_end_next_day
        )
        Subject.objects.create(name='Subject', user=user_obj, description='Subject description')

        cls.start = time(hour=21, minute=10)
        cls.end = time(hour=23, minute=10)
        cls.end_next_day = False
        cls.duration = time_diff_in_seconds(cls.start, cls.end, cls.end_next_day)

        cls.day_time_usage_ratio = Decimal(cls.duration / cls.day_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

    def test_session_create_with_end_time(self):
        """Test the case when a session, whose end time and end next day are specified, is created. """
        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
            end=TestSession.end,
            end_next_day=TestSession.end_next_day,
        )
        session_obj = Session.objects.get(start=TestSession.start)

        # Check session
        self.assertEqual(session_obj.start, TestSession.start, 'Wrong start time')
        self.assertEqual(session_obj.end, TestSession.end, 'Wrong end time')
        self.assertEqual(session_obj.end_next_day, TestSession.end_next_day, 'Wrong end next day')
        self.assertEqual(session_obj.duration, TestSession.duration, 'Wrong duration')

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 1, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            TestSession.duration,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            TestSession.day_time_usage_ratio,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            TestSession.duration,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            1,
            'Wrong session count of the associated subject'
        )

    def test_session_create_no_end_time(self):
        """Test the case when a session, whose end time and end next day are not specified, is created. """

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
        )
        session_obj = Session.objects.get(start=TestSession.start)

        # Check session
        self.assertEqual(session_obj.start, TestSession.start, 'Wrong start time')
        self.assertEqual(session_obj.end, None, 'Wrong end time')
        self.assertEqual(session_obj.end_next_day, False, 'Wrong end next day')
        self.assertEqual(session_obj.duration, 0, 'Wrong duration')

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 1, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            0,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            0,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            0,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            1,
            'Wrong session count of the associated subject'
        )

    def test_session_create_end_next_day(self):
        """Test the case when a session which ends the next day is created. """

        end = time(hour=0, minute=10)
        end_next_day = True
        duration = time_diff_in_seconds(TestSession.start, end, end_next_day)
        day_time_usage_ratio = Decimal(duration / TestSession.day_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
            end=end,
            end_next_day=end_next_day,
        )
        session_obj = Session.objects.get(start=TestSession.start)

        # Check session
        self.assertEqual(session_obj.start, TestSession.start, 'Wrong start time')
        self.assertEqual(session_obj.end, end, 'Wrong end time')
        self.assertEqual(session_obj.end_next_day, end_next_day, 'Wrong end next day')
        self.assertEqual(session_obj.duration, duration, 'Wrong duration')

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 1, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            duration,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            day_time_usage_ratio,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            duration,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            1,
            'Wrong session count of the associated subject'
        )

    def test_session_update_change_end_time(self):
        """
        Test the case when a session with end time and end next day specified is updated by changing these two fields.
        """

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
            end=TestSession.end,
            end_next_day=TestSession.end_next_day,
        )

        new_date = TestSession.day + timedelta(days=1)
        new_day_of_week = new_date.isoweekday()
        new_day = Day.objects.create(
            user=User.objects.get(username='fx'),
            stage=Stage.objects.get(name='Stage'),
            day=new_date,
            worktime=TestSession.day_worktime,
            start=TestSession.day_start,
            end=TestSession.day_end,
            end_next_day=TestSession.day_end_next_day,
        )
        new_subject = Subject.objects.create(
            name='Subject 2',
            user=User.objects.get(username='fx'),
            description='Subject 2 description'
        )
        new_start = time(hour=20, minute=10)
        new_end = time(hour=22, minute=10)
        new_end_next_day = False
        new_duration = time_diff_in_seconds(new_start, new_end, new_end_next_day)
        new_day_time_usage_ratio = Decimal(new_duration / TestSession.day_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

        session_obj = Session.objects.get(start=TestSession.start)
        session_obj.day = new_day
        session_obj.subject = new_subject
        session_obj.start = new_start
        session_obj.end = new_end
        session_obj.end_next_day = new_end_next_day
        session_obj.save()
        session_obj = Session.objects.get(start=new_start)

        # Check session
        self.assertEqual(session_obj.start, new_start, 'Wrong start time')
        self.assertEqual(session_obj.end, new_end, 'Wrong end time')
        self.assertEqual(session_obj.end_next_day, new_end_next_day, 'Wrong end next day')
        self.assertEqual(session_obj.duration, new_duration, 'Wrong duration')

        # Check old day
        old_day = Day.objects.get(day=TestSession.day)
        self.assertEqual(old_day.day, TestSession.day, 'Wrong date of the previous associated day')
        self.assertEqual(old_day.day_of_week, TestSession.day_of_week, 'Wrong date of the previous associated day')
        self.assertEqual(old_day.session_count, 0, 'Wrong session count of the previous associated day')
        self.assertEqual(old_day.worktime, TestSession.day_worktime, 'Wrong work time of the previous associated day')
        self.assertEqual(old_day.start, TestSession.day_start, 'Wrong start time of the previous associated day')
        self.assertEqual(old_day.end, TestSession.day_end, 'Wrong end time of the previous associated day')
        self.assertEqual(
            old_day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the previous associated day'
        )
        self.assertEqual(
            old_day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the previous associated day'
        )
        self.assertEqual(
            old_day.study_time,
            0,
            'Wrong study time of the previous associated day'
        )
        self.assertEqual(
            old_day.time_usage_ratio,
            0,
            'Wrong time usage ratio of the previous associated day'
        )

        # Check new day
        self.assertEqual(session_obj.day.day, new_date, 'Wrong date of the new associated day')
        self.assertEqual(session_obj.day.day_of_week, new_day_of_week, 'Wrong date of the new associated day')
        self.assertEqual(session_obj.day.session_count, 1, 'Wrong session count of the new associated day')
        self.assertEqual(
            session_obj.day.worktime,
            TestSession.day_worktime,
            'Wrong work time of the new associated day'
        )
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the new associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the new associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the new associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the new associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            new_duration,
            'Wrong study time of the new associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            new_day_time_usage_ratio,
            'Wrong time usage ratio of the new associated day'
        )

        # Check old subject
        old_subject = Subject.objects.get(name='Subject')
        self.assertEqual(
            old_subject.total_study_time,
            0,
            'Wrong total study time of the previous associated subject'
        )
        self.assertEqual(
            old_subject.session_count,
            0,
            'Wrong session count of the previous associated subject'
        )

        # Check new subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            new_duration,
            'Wrong total study time of the new associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            1,
            'Wrong session count of the new associated subject'
        )

    def test_session_update_add_end_time(self):
        """Test the case when a session without end time and end next day is updated by specifying these two fields. """

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
        )

        new_end = time(hour=0, minute=10)
        new_end_next_day = True
        new_duration = time_diff_in_seconds(TestSession.start, new_end, new_end_next_day)
        new_day_time_usage_ratio = Decimal(new_duration / TestSession.day_usable_time) \
            .quantize(Decimal('.0001'), rounding=ROUND_HALF_EVEN)

        session_obj = Session.objects.get(start=TestSession.start)
        session_obj.start = TestSession.start
        session_obj.end = new_end
        session_obj.end_next_day = new_end_next_day
        session_obj.save()
        session_obj = Session.objects.get(start=TestSession.start)

        # Check session
        self.assertEqual(session_obj.start, TestSession.start, 'Wrong start time')
        self.assertEqual(session_obj.end, new_end, 'Wrong end time')
        self.assertEqual(session_obj.end_next_day, new_end_next_day, 'Wrong end next day')
        self.assertEqual(session_obj.duration, new_duration, 'Wrong duration')

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 1, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            new_duration,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            new_day_time_usage_ratio,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            new_duration,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            1,
            'Wrong session count of the associated subject'
        )

    def test_session_update_remove_end_time(self):
        """Test the case when a session whose end time and end next day were specified and are now removed. """

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
            end=TestSession.end,
            end_next_day=TestSession.end_next_day,
        )

        new_end = None
        new_end_next_day = None
        new_duration = 0
        new_day_time_usage_ratio = 0

        session_obj = Session.objects.get(start=TestSession.start)
        session_obj.end = new_end
        session_obj.end_next_day = new_end_next_day
        session_obj.save()
        session_obj = Session.objects.get(start=TestSession.start)

        # Check session
        self.assertEqual(session_obj.start, TestSession.start, 'Wrong start time')
        self.assertEqual(session_obj.end, new_end, 'Wrong end time')
        self.assertEqual(session_obj.end_next_day, new_end_next_day, 'Wrong end next day')
        self.assertEqual(session_obj.duration, new_duration, 'Wrong duration')

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 1, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            new_duration,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            new_day_time_usage_ratio,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            new_duration,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            1,
            'Wrong session count of the associated subject'
        )

    def test_session_delete_with_end_time(self):
        """Test the case when a session with end time and end next day specified is deleted."""

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
            end=TestSession.end,
            end_next_day=TestSession.end_next_day,
        )
        session_obj = Session.objects.get(start=TestSession.start)
        session_obj.delete()

        # Check session
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            Session.objects.get(start=TestSession.start)

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 0, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            0,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            0,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            0,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            0,
            'Wrong session count of the associated subject'
        )

    def test_session_delete_no_end_time(self):
        """Test the case when a session with end time and end next day unspecified is deleted. """

        Session.objects.create(
            user=User.objects.get(username=TestSession.username),
            day=Day.objects.get(day=TestSession.day),
            subject=Subject.objects.get(name='Subject'),
            start=TestSession.start,
        )
        session_obj = Session.objects.get(start=TestSession.start)
        session_obj.delete()

        # Check session
        with self.assertRaises(ObjectDoesNotExist, msg='Wrong does not exist exception'):
            Session.objects.get(start=TestSession.start)

        # Check day
        self.assertEqual(session_obj.day.day, TestSession.day, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.day_of_week, TestSession.day_of_week, 'Wrong date of the associated day')
        self.assertEqual(session_obj.day.session_count, 0, 'Wrong session count of the associated day')
        self.assertEqual(session_obj.day.worktime, TestSession.day_worktime, 'Wrong work time of the associated day')
        self.assertEqual(session_obj.day.start, TestSession.day_start, 'Wrong start time of the associated day')
        self.assertEqual(session_obj.day.end, TestSession.day_end, 'Wrong end time of the associated day')
        self.assertEqual(
            session_obj.day.end_next_day,
            TestSession.day_end_next_day,
            'Wrong end next day of the associated day'
        )
        self.assertEqual(
            session_obj.day.usable_time,
            TestSession.day_usable_time,
            'Wrong usable time of the associated day'
        )
        self.assertEqual(
            session_obj.day.study_time,
            0,
            'Wrong study time of the associated day'
        )
        self.assertEqual(
            session_obj.day.time_usage_ratio,
            0,
            'Wrong time usage ratio of the associated day'
        )

        # Check subject
        self.assertEqual(
            session_obj.subject.total_study_time,
            0,
            'Wrong total study time of the associated subject'
        )
        self.assertEqual(
            session_obj.subject.session_count,
            0,
            'Wrong session count of the associated subject'
        )
