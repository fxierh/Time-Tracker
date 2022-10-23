from datetime import date, time
from decimal import Decimal
from itertools import product

from django.contrib.auth import get_user_model
from django.db.models import Max
from django.db.models.functions import Coalesce
from django.test import TestCase, SimpleTestCase, Client
from django.urls import reverse
from numpy import cumsum

from ..models import Session, User, Stage, Subject, Day
from ..templatetags.filters import ratio_to_percentage
from ..views import seconds_to_hours_minutes, hours_to_hours_minutes, cumsum_in_place, time_to_idx, get_freq_list


class TestSecondsToHoursMinutes(SimpleTestCase):
    """Test the seconds_to_hours_minutes function. """

    def test_typical_usage(self):
        """Test typical use case (i.e. non zero input). """

        hour, minute, second = 25, 13, 55
        s = hour * 3600 + minute * 60 + second
        self.assertEqual(seconds_to_hours_minutes(s), f'{hour}h, {minute}min', 'Wrong output')

    def test_zero_input(self):
        self.assertEqual(seconds_to_hours_minutes(0), '0h, 0min', 'Wrong output')


class TestHoursToHoursMinutes(SimpleTestCase):
    """Test the hours_to_hours_minutes function. """

    def test_typical_usage(self):
        """Test typical use case (i.e. non zero input). """

        integral_hour, fractional_hour = 25, 0.13
        minute = round(fractional_hour * 60)
        self.assertEqual(
            hours_to_hours_minutes(integral_hour + fractional_hour),
            f'{integral_hour}h, {minute}min',
            'Wrong output'
        )

    def test_zero_input(self):
        self.assertEqual(hours_to_hours_minutes(0), f'{0}h, {0}min', 'Wrong output')


class TestCumsumInPlace(SimpleTestCase):
    """Test the cumsum_in_place function. """

    def test_typical_usage(self):
        """Test typical usage. """

        lst = [1, -1, 2, -3, 5, -8, 13, -21, 34]
        numpy_output = cumsum(lst).tolist()
        cumsum_in_place(lst)
        self.assertEqual(lst, numpy_output, 'Wrong output')


class TestTimeToIndex(SimpleTestCase):
    """Test the time_to_index function. """

    def test_typical_usage(self):
        """Test typical usage, i.e. the input time is not close to midnight. """

        t = time(23, 15)
        n_step_per_hour = 4

        self.assertEqual(time_to_idx(t, n_step_per_hour), (False, 93), 'Wrong output')

    def test_close_to_midnight(self):
        """
        Test the case when the input time is close to midnight, making sure the output index is 0 and not out of range.
        """

        t = time(23, 59)
        n_step_per_hour = 4

        self.assertEqual(time_to_idx(t, n_step_per_hour), (True, 0), 'Wrong output')


class TestGetFreqList(TestCase):
    """Test the get_freq_list function. """

    def setUp(self):
        self.user = User.objects.create(
            username='fx',
            email='123@gmail.com',
        )
        self.stage = Stage.objects.create(
            user=self.user,
            name='Stage'
        )
        self.day = Day.objects.create(
            user=self.user,
            stage=self.stage,
            day=date(2022, 5, 6),
            start=time(10, 10)
        )
        self.subject = Subject.objects.create(
            user=self.user,
            name='Subject'
        )

    def test_typical_usage(self):
        """Test typical usage, i.e. no session with duration >= 24 hours, and no session ends near midnight. """

        n_steps_per_hour = 4

        min_per_step = 60 // n_steps_per_hour
        total_nb_steps = 24 * n_steps_per_hour
        freq_list = [0] * total_nb_steps

        hours = range(24)
        minutes = range(0, 60, min_per_step)
        times = list(product(hours, minutes))

        objects_to_create = []

        for i, (start_hour, start_minute) in enumerate(times):
            for j in range(total_nb_steps):
                end_hour, end_minute = times[j]
                start = time(start_hour, start_minute)
                end = time(end_hour, end_minute)

                if i <= j:
                    for idx in range(time_to_idx(start, n_steps_per_hour)[1], time_to_idx(end, n_steps_per_hour)[1] + 1):
                        freq_list[idx] += 1
                else:
                    for idx in range(time_to_idx(start, n_steps_per_hour)[1], total_nb_steps):
                        freq_list[idx] += 1
                    for idx in range(0, time_to_idx(end, n_steps_per_hour)[1] + 1):
                        freq_list[idx] += 1

                objects_to_create.append(
                    Session(
                        user=self.user,
                        day=self.day,
                        subject=self.subject,
                        start=start,
                        end=end,
                        end_next_day=False if j >= i else True,
                    )
                )

        Session.objects.bulk_create(objects_to_create)

        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong frequency list'
        )

    def test_session_between_24_and_48h(self):
        """
        Test the case when a session lasts between 24 hours (inclusive) and 48 hours (exclusive),
        but does not end near midnight.
        """

        n_steps_per_hour = 4
        freq_list = [1] * 24 * n_steps_per_hour
        start = time(10, 10)
        end = time(12, 5)

        for idx in range(time_to_idx(start, n_steps_per_hour)[1], time_to_idx(end, n_steps_per_hour)[1] + 1):
            freq_list[idx] += 1

        Session.objects.create(
            user=self.user,
            day=self.day,
            subject=self.subject,
            start=start,
            end=end,
            end_next_day=True,
        )

        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong frequency list'
        )

    def test_end_close_to_midnight(self):
        """Test the case when a session ends close to midnight. """

        n_steps_per_hour = 4
        total_nb_steps = 24 * n_steps_per_hour
        freq_list = [0] * total_nb_steps
        start = time(22, 00)
        end = time(23, 59)

        _, start_idx = time_to_idx(start, n_steps_per_hour)
        idx_overflow, end_idx = time_to_idx(end, n_steps_per_hour)
        self.assertTrue(idx_overflow, 'Index should overflow and becomes 0')

        for idx in range(start_idx, total_nb_steps):
            freq_list[idx] += 1
        for idx in range(0, end_idx + 1):
            freq_list[idx] += 1

        Session.objects.create(
            user=self.user,
            day=self.day,
            subject=self.subject,
            start=start,
            end=end,
            end_next_day=False,
        )

        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong frequency list'
        )

    def test_no_session(self):
        """Test the case when the user has no session. """

        n_steps_per_hour = 4
        freq_list = [0] * 24 * n_steps_per_hour

        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong frequency list'
        )

    def test_uncompleted_session(self):
        """Test the case that uncompleted sessions (i.e. those without end time for ex.)
        are not accounted for in the freq list. """

        n_steps_per_hour = 4
        freq_list = [0] * 24 * n_steps_per_hour

        # Session with no end time should not be accounted for in the freq list
        Session.objects.create(
            user=self.user,
            day=self.day,
            subject=self.subject,
            start=time(22, 00),
            end_next_day=False,
        )
        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong frequency list'
        )
        Session.objects.all().delete()

        # Session with end_next_day=None should not be accounted for in the freq list
        Session.objects.create(
            user=self.user,
            day=self.day,
            subject=self.subject,
            start=time(21, 00),
            end=time(23, 00),
            end_next_day=None,
        )

        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong frequency list'
        )


class TestDashboardView(TestCase):
    """Test the dashboard view. """

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='user',
            password='user_password',
        )
        self.stage = Stage.objects.create(
            user=self.user,
            name='Stage'
        )
        self.subject = Subject.objects.create(
            user=self.user,
            name='Subject'
        )
        self.day = Day.objects.create(
            user=self.user,
            stage=self.stage,
            day=date(2022, 5, 6),
            worktime=2 * 3600,
            start=time(10, 0),
            end=time(1, 0),
            end_next_day=True,
        )
        self.session = Session.objects.create(
            user=self.user,
            day=self.day,
            subject=self.subject,
            start=time(12, 0),
            end=time(14, 0),
            end_next_day=False,
        )
        self.url = reverse('classic_tracker:dashboard')
        self.client.force_login(self.user)

    def test_login_required(self):
        """Test making sure anonymous users are redirect to the login page. """

        self.client.logout()
        res = self.client.get(self.url)
        self.assertRedirects(res, f'/accounts/login/?next={self.url}')

    def test_context_data(self):
        """Test that the correct context data are in the html. """

        # Study distribution data
        n_steps_per_hour = 4
        freq_list = [0] * 24 * n_steps_per_hour
        for idx in range(
                time_to_idx(self.session.start, n_steps_per_hour)[1],
                time_to_idx(self.session.end, n_steps_per_hour)[1] + 1
        ):
            freq_list[idx] += 1
        data_study = 'data_study = ' + str(freq_list)

        # Global data
        total_usable_time = round(self.user.total_usable_time / 3600, 1)
        total_work_time = round(self.user.total_work_time / 3600, 1)
        total_study_time = round(self.user.total_study_time / 3600, 1)
        non_study_time = max(0, total_usable_time - total_study_time)
        inactive_time = self.user.day_count * 24 - total_study_time - non_study_time - total_work_time
        data_global = 'data_global = ' + str([
            total_work_time,
            total_study_time,
            non_study_time,
            inactive_time,
        ])

        res = self.client.get(self.url)
        self.assertContains(res, data_study)
        self.assertContains(res, data_global)

    def test_global_analytics(self):
        """Test that the global analytics table contains the correct data. """

        variables = [
            'Stage count',
            'Day count',
            'Session count',
            'Subject count',
            'Total usable time',
            'Total study time',
            'Total work time',
            'Max usable time',
            'Max study time',
            'Max time usage percentage',
            'Average session time',
            'Average day time',
            'Time usage percentage',
            'Study work ratio'
        ]

        aggregate_data = Day.objects.aggregate(
            max_usable_time=Coalesce(Max('usable_time'), 0),
            max_study_time=Coalesce(Max('study_time'), 0),
            max_time_usage_ratio=Coalesce(Max('time_usage_ratio'), Decimal(0))
        )

        values = [
            self.user.stage_count,
            self.user.day_count,
            self.user.session_count,
            self.user.subject_count,
            seconds_to_hours_minutes(self.user.total_usable_time),
            seconds_to_hours_minutes(self.user.total_study_time),
            seconds_to_hours_minutes(self.user.total_work_time),
            seconds_to_hours_minutes(aggregate_data['max_usable_time']),
            seconds_to_hours_minutes(aggregate_data['max_study_time']),
            ratio_to_percentage(aggregate_data['max_time_usage_ratio']),
            seconds_to_hours_minutes(self.user.total_study_time / self.user.session_count),
            seconds_to_hours_minutes(self.user.total_study_time / self.user.day_count),
            ratio_to_percentage(self.user.total_study_time / self.user.total_usable_time),
            round(self.user.total_study_time / self.user.total_work_time, 1)
        ]

        table_row_regex_list = []
        for var, val in zip(variables, values):
            table_row_regex_list.append(fr'<tr>\n\s*<td>{var}</td>\n\s*<td>{val}</td>\n\s*</tr>')

        res = self.client.get(self.url)
        for table_row_regex in table_row_regex_list:
            self.assertRegex(res.content.decode(), table_row_regex)


class TestDayCreateView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='user',
            password='user_password',
        )
        self.stage = Stage.objects.create(
            user=self.user,
            name='Stage'
        )
        self.url = reverse('classic_tracker:create_day')
        self.client.force_login(self.user)

    def test_login_required(self):
        """Test making sure anonymous users are redirect to the login page. """

        self.client.logout()
        res = self.client.get(self.url)
        self.assertRedirects(res, f'/accounts/login/?next={self.url}')

    def test_day_create_success(self):
        """Test the case when a day is successfully created. """

        # By default, the test client disables any CSRF checks
        res = self.client.post(self.url, data={
            'day': ['2022-10-22'],
            'stage': [self.stage.pk],
            'worktime_hour': ['2'],
            'worktime_minute': ['0'],
            'start': ['10:44'],
            'end': ['01:44'],
            'end_next_day': ['true'],
            'comment': ['Some Comment']
        })

        # Redirect
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('thank_you'))

        # Make sure the Day object is saved
        self.assertTrue(Day.objects.filter(day=date(year=2022, month=10, day=22)).exists())

        # Computed fields
        day = Day.objects.get(day=date(year=2022, month=10, day=22))
        self.assertEqual(day.user, self.user)
        self.assertEqual(day.usable_time, 13 * 3600)
        self.assertEqual(day.day_of_week, day.day.isoweekday())

        self.assertEqual(day.stage.day_count, 1)
        self.assertEqual(day.stage.total_usable_time, day.usable_time)
        self.assertEqual(day.stage.total_work_time, day.worktime)

        self.assertEqual(day.user.day_count, 1)
        self.assertEqual(day.user.total_usable_time, day.usable_time)
        self.assertEqual(day.user.total_work_time, day.worktime)


class TestDayListView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='user',
            password='user_password',
        )
        self.stage1 = Stage.objects.create(
            user=self.user,
            name='Stage1'
        )
        self.stage2 = Stage.objects.create(
            user=self.user,
            name='Stage2'
        )
        self.day1 = Day.objects.create(
            user=self.user,
            stage=self.stage1,
            day=date(2022, 5, 6),
            worktime=2 * 3600,
            start=time(10, 0),
            end=time(1, 0),
            end_next_day=True,
        )
        self.day2 = Day.objects.create(
            user=self.user,
            stage=self.stage2,
            day=date(2022, 5, 7),
            worktime=2 * 3600,
            start=time(10, 0),
            end=time(1, 0),
            end_next_day=True,
        )
        self.url = reverse('classic_tracker:list_day')
        self.client.force_login(self.user)

    def test_login_required(self):
        """Test making sure anonymous users are redirect to the login page. """

        self.client.logout()
        res = self.client.get(self.url)
        self.assertRedirects(res, f'/accounts/login/?next={self.url}')

    def test_days_listed(self):
        """Test making sure the day objects are listed. """

        res = self.client.get(self.url)
        self.assertContains(res, self.day1.day.strftime('%b %-d, %Y'))
        self.assertContains(res, self.day2.day.strftime('%b %-d, %Y'))

    def test_sort(self):
        """Test the sort functionality. """

        res = self.client.get(self.url + '?sorting=day')
        self.assertLess(
            res.content.decode().find(self.day1.day.strftime('%b %-d, %Y')),
            res.content.decode().find(self.day2.day.strftime('%b %-d, %Y'))
        )

        res = self.client.get(self.url + '?sorting=-day')
        self.assertGreater(
            res.content.decode().find(self.day1.day.strftime('%b %-d, %Y')),
            res.content.decode().find(self.day2.day.strftime('%b %-d, %Y'))
        )

    def test_filter_by_stage(self):
        """Test the filter by stage functionality. """

        res = self.client.get(self.url + f'?stage={self.stage1.pk}')
        self.assertContains(res, self.day1.day.strftime('%b %-d, %Y'))
        self.assertNotContains(res, self.day2.day.strftime('%b %-d, %Y'))


class TestDayUpdateView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='user',
            password='user_password',
        )
        self.stage = Stage.objects.create(
            user=self.user,
            name='Stage'
        )
        self.day = Day.objects.create(
            user=self.user,
            stage=self.stage,
            day=date(2022, 5, 6),
            worktime=3600,
            start=time(10, 0),
            end=time(1, 0),
            end_next_day=True,
        )
        self.url = reverse('classic_tracker:update_day', args=(self.day.pk,))
        self.client.force_login(self.user)

    def test_login_required(self):
        """Test making sure anonymous users are redirect to the login page. """

        self.client.logout()
        res = self.client.get(self.url)
        self.assertRedirects(res, f'/accounts/login/?next={self.url}')

    def test_day_update_success(self):
        """Test the case when a day is successfully updated. """

        # Get request
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        # Post request
        res = self.client.post(self.url, data={
            'day': ['2022-10-22'],
            'stage': [self.stage.pk],
            'worktime_hour': ['2'],
            'worktime_minute': ['0'],
            'start': ['10:44'],
            'end': ['01:44'],
            'end_next_day': ['true'],
            'comment': ['Some Comment']
        })

        # Redirect
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('thank_you'))

        # Make sure the Day object is saved
        self.assertTrue(Day.objects.filter(day=date(year=2022, month=10, day=22)).exists())

        # Computed fields
        day = Day.objects.get(day=date(year=2022, month=10, day=22))
        self.assertEqual(day.user, self.user)
        self.assertEqual(day.usable_time, 13 * 3600)
        self.assertEqual(day.day_of_week, day.day.isoweekday())

        self.assertEqual(day.stage.day_count, 1)
        self.assertEqual(day.stage.total_usable_time, day.usable_time)
        self.assertEqual(day.stage.total_work_time, day.worktime)

        self.assertEqual(day.user.day_count, 1)
        self.assertEqual(day.user.total_usable_time, day.usable_time)
        self.assertEqual(day.user.total_work_time, day.worktime)


class TestDayDeleteView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            username='user',
            password='user_password',
        )
        self.stage = Stage.objects.create(
            user=self.user,
            name='Stage'
        )
        self.day = Day.objects.create(
            user=self.user,
            stage=self.stage,
            day=date(2022, 5, 6),
            worktime=3600,
            start=time(10, 0),
            end=time(1, 0),
            end_next_day=True,
        )
        self.url = reverse('classic_tracker:delete_day', args=(self.day.pk,))
        self.client.force_login(self.user)

    def test_login_required(self):
        """Test making sure anonymous users are redirect to the login page. """

        self.client.logout()
        res = self.client.get(self.url)
        self.assertRedirects(res, f'/accounts/login/?next={self.url}')

    def test_day_delete_success(self):
        """Test the case when a day is successfully deleted. """

        # Get request
        res = self.client.get(self.url)
        self.assertContains(res, 'Delete a day results in the deletion of all its sessions')
        self.assertEqual(res.status_code, 200)

        # Post request
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('thank_you'))
        self.assertFalse(Day.objects.exists())
