from datetime import date, time
from itertools import product

from django.test import TestCase, SimpleTestCase
from numpy import cumsum

from ..models import Session, User, Stage, Subject, Day
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
            'Wrong output'
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
            'Wrong output'
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
            'Wrong output'
        )

    def test_no_session(self):
        """Test the case when the user has no session. """

        n_steps_per_hour = 4
        freq_list = [0] * 24 * n_steps_per_hour

        self.assertEqual(
            get_freq_list(Session.objects.values_list('start', 'end', 'end_next_day'), n_steps_per_hour),
            freq_list,
            'Wrong output'
        )
