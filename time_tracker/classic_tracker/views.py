from datetime import time
from decimal import Decimal
from math import ceil
from typing import List, Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import caches
from django.core.cache.utils import make_template_fragment_key
from django.db.models import Max, QuerySet, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView

from .forms import DayCreateUpdateForm, SessionCreateUpdateForm, StageCreateUpdateForm, SubjectCreateUpdateForm
from .models import Day, Session, Stage, Subject


def seconds_to_hours_minutes(s: Optional[int]) -> str:
    """
    Conversion from (X s) to (Yh, Zmin).

    :param s: duration in seconds
    """

    s = int(s)

    assert s >= 0, 'Integer input must be non negative'

    # get min and seconds first
    m, s = divmod(s, 60)

    # Get hours
    h, m = divmod(m, 60)
    return f'{(int(h))}h, {int(m)}min'


def hours_to_hours_minutes(h: float) -> str:
    """
    Conversion from (X.Y hours) to (Zh, Amin).

    :param h: number of hours as a float
    """

    assert h >= 0, 'The input must be non negative'

    return f'{int(h)}h, {round((h - int(h)) * 60)}min'


def cumsum_in_place(l: List[int]) -> None:
    """
    This function converts a list to its cumsum, in place. \n
    Example: [1, 3, 5, 7, 9] becomes [1, 4, 9, 16, 25]
    """

    cumsum = 0
    for i, ele in enumerate(l):
        cumsum += ele
        l[i] = cumsum
    return


def time_to_idx(t: time, n_steps_per_hour: int) -> (bool, int):
    """
    The first output indicates if the input time is too close to midnight s.t. the index overflows and becomes 0.
    The second output is the index (in the frequency list, which is used in the dashboard plot) corresponds to a time.

    Example: if the frequency list is quantized s.t. it has 4 steps per hour,
    then 2:15 AM corresponds to index 2 * 4 + 15 * 4 / 60 = 9 in the frequency list.
    """

    # Attention: Python's round function rounds to the nearest even integer
    return divmod(t.hour * n_steps_per_hour + round(t.minute * n_steps_per_hour / 60), n_steps_per_hour * 24)


def get_freq_list(user_sessions: QuerySet, n_steps_per_hour: int = 4) -> list:
    """
    This function returns a frequency list, which is required by Chart.js for plotting.
    If user has no sessions, returns an empty list.

    Time = O(n_sessions + n_steps_per_day), space = O(n_steps_per_day)

    :param user_sessions: user_sessions.values_list('start', 'end', 'end_next_day')
    :param n_steps_per_hour: number of steps per hour in the dashboard plot.
    :return: a list of frequencies, i.e. a list containing the bars' heights
    """

    assert 60 % int(n_steps_per_hour) == 0, \
        "60 should be divisible by n_steps_per_hour, i.e. step size in minutes should be an integer"

    n_steps_per_day = n_steps_per_hour * 24
    times = [0] * n_steps_per_day

    # Populate the 2 frequency lists
    for session in user_sessions:
        start, end, end_next_day = session

        # If session is well-defined (relative to to-be-completed), update the frequency lists
        if start is not None and end is not None and end_next_day is not None:

            if end_next_day:
                times[0] += 1

            times[time_to_idx(start, n_steps_per_hour)[1]] += 1

            # Avoid end_idx out of range
            idx_overflow, end_idx = time_to_idx(end, n_steps_per_hour)
            if end_idx + 1 < n_steps_per_day:
                times[end_idx + 1] -= 1

            if idx_overflow:
                times[0] += 1

    # Turn the frequency list into cumsum list
    cumsum_in_place(times)

    return times


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'classic_tracker/dashboard.html'

    # Extra context variables to display
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_sessions = Session.objects.filter(user=self.request.user.id).values_list('start', 'end', 'end_next_day')

        # Compute max then normalize
        context.update(
            Day.objects.filter(user=self.request.user.id).aggregate(
                max_usable_time=Coalesce(Max('usable_time'), 0),
                max_study_time=Coalesce(Max('study_time'), 0),
                max_time_usage_ratio=Coalesce(Max('time_usage_ratio'), Decimal(0))
            )
        )

        # Data for time distribution pie chart
        context['time_distribution_labels'] = [
            'Work time (h)',
            'Study time (h)',
            'Non study time (h)',
            'Inactive time (h)'
        ]

        total_usable_time = round(self.request.user.total_usable_time / 3600, 1)  # In hours, same below
        total_work_time = round(self.request.user.total_work_time / 3600, 1)
        total_study_time = round(self.request.user.total_study_time / 3600, 1)
        non_study_time = max(0, total_usable_time - total_study_time)
        inactive_time = self.request.user.day_count * 24 - total_study_time - non_study_time - total_work_time
        context['time_distribution_data'] = [
            total_work_time,
            total_study_time,
            non_study_time,
            inactive_time
        ]

        # Data for study time distribution bar plot
        n_steps_per_hour = 4
        min_per_step = 60 // n_steps_per_hour
        context['study_time_distribution_data'] = get_freq_list(user_sessions, n_steps_per_hour)
        bar_plot_labels = [''] * (n_steps_per_hour * 24)
        for step in range(24 * n_steps_per_hour):
            hour, n_step = divmod(step, n_steps_per_hour)
            if n_step > 0:
                bar_plot_labels[step] = f'{hour}h{n_step * min_per_step}'
            else:
                bar_plot_labels[step] = f'{hour}h'
        context['study_time_distribution_labels'] = bar_plot_labels

        return context


class DayCreateView(LoginRequiredMixin, CreateView):
    model = Day
    form_class = DayCreateUpdateForm  # Customized form
    success_url = reverse_lazy('thank_you')

    def form_valid(self, form):
        # Get day object
        obj = form.save(commit=False)

        # Automatically fill the user field of day.
        # Note: obj will be saved later when super().form_valid(form) is called
        obj.user = self.request.user

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form
        kwargs['user'] = self.request.user
        return kwargs


class DayListView(LoginRequiredMixin, ListView):
    model = Day
    # Customize the name of the object_list sent to template
    context_object_name = 'day_list'
    paginate_by = 10

    def get_queryset(self):
        sorting = self.request.GET.get('sorting', default='-id')
        stage = self.request.GET.get('stage', default=None)

        queryset = Day.objects.filter(user=self.request.user.id)
        if stage is not None:
            queryset = queryset.filter(stage=stage)

        # Annotate is a performance booster which results in a single more complex query
        # but means later use of foreign-key relationships won’t require database queries.
        queryset = queryset\
            .annotate(id_stage=F('stage__id'), name_stage=F('stage__name'))\
            .order_by(sorting)

        return queryset


class DayUpdateView(LoginRequiredMixin, UpdateView):
    model = Day
    form_class = DayCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form
        kwargs['user'] = self.request.user
        return kwargs


class DayDeleteView(LoginRequiredMixin, DeleteView):
    model = Day
    success_url = reverse_lazy('thank_you')


class DayDetailView(LoginRequiredMixin, DetailView):
    model = Day

    # Extra context variables to display
    def get_context_data(self, **kwargs):
        day_obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context['sessions'] = Session.objects.filter(day=day_obj)

        # Unit conversion
        context['usable_time'] = seconds_to_hours_minutes(day_obj.usable_time)
        context['study_time'] = seconds_to_hours_minutes(day_obj.study_time)
        context['work_time'] = seconds_to_hours_minutes(day_obj.worktime)
        context['time_usage_percentage'] = round(day_obj.time_usage_ratio * 100, 1)
        return context


class SessionCreateView(LoginRequiredMixin, CreateView):
    model = Session
    form_class = SessionCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def form_valid(self, form):
        # Get session object
        obj = form.save(commit=False)

        # Automatically fill the user field of session
        # Note: obj will be saved later when super().form_valid(form) is called
        obj.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form, so that the dropdown menu is filtered
        # and only contains day and subject of the current user.
        kwargs['user'] = self.request.user
        return kwargs


class SessionListView(LoginRequiredMixin, ListView):
    model = Session
    # Customize the name of the object_list sent to template
    context_object_name = 'session_list'
    paginate_by = 10

    def get_queryset(self):
        sorting = self.request.GET.get('sorting', default='-id')
        day = self.request.GET.get('day', default=None)
        subject = self.request.GET.get('subject', default=None)

        queryset = Session.objects.filter(user=self.request.user.id)

        if day:
            queryset = queryset.filter(day=day)

        if subject:
            queryset = queryset.filter(subject=subject)

        return queryset\
            .annotate(date=F('day__day'), day_of_week=F('day__day_of_week'), name_subject=F('subject__name'))\
            .order_by(sorting)


class SessionUpdateView(LoginRequiredMixin, UpdateView):
    model = Session
    form_class = SessionCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form, so that the dropdown menu is filtered
        # and only contains day and subject of the current user.
        kwargs['user'] = self.request.user
        return kwargs


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = Session
    success_url = reverse_lazy('thank_you')


class SessionDetailView(LoginRequiredMixin, DetailView):
    model = Session

    # Extra context variables to display
    def get_context_data(self, **kwargs):
        session_obj = self.get_object()
        context = super().get_context_data(**kwargs)
        if session_obj.duration:
            # Conversion from seconds to hours minutes
            context['duration'] = seconds_to_hours_minutes(session_obj.duration)
        return context


class StageCreateView(LoginRequiredMixin, CreateView):
    model = Stage
    form_class = StageCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def form_valid(self, form):
        # Get stage object
        obj = form.save(commit=False)

        # Automatically fill the user field
        # Note: obj will be saved later when super().form_valid(form) is called
        obj.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form
        kwargs['user'] = self.request.user
        return kwargs


class StageListView(LoginRequiredMixin, ListView):
    model = Stage
    # Customize the name of the object_list sent to template
    context_object_name = 'stage_list'

    def get_queryset(self):
        # Compute maximums
        # The 1st .values() is equivalent to group by, the 2nd .values() selects one column to output
        day_max_work_time = Day.objects \
            .filter(stage=OuterRef('id')) \
            .values('stage__id') \
            .annotate(max_work_time=(Max('worktime'))) \
            .values('max_work_time')

        day_max_usable_time = Day.objects \
            .filter(stage=OuterRef('id')) \
            .values('stage__id') \
            .annotate(max_usable_time=(Max('usable_time'))) \
            .values('max_usable_time')

        day_max_study_time = Day.objects \
            .filter(stage=OuterRef('id')) \
            .values('stage__id') \
            .annotate(max_study_time=Max('study_time')) \
            .values('max_study_time')

        day_max_time_usage_ratio = Day.objects \
            .filter(stage=OuterRef('id')) \
            .values('stage__id') \
            .annotate(max_time_usage_ratio=Max('time_usage_ratio')) \
            .values('max_time_usage_ratio')

        return Stage.objects\
            .filter(user=self.request.user.id)\
            .annotate(
                max_work_time=Coalesce(Subquery(day_max_work_time), 0),
                max_usable_time=Coalesce(Subquery(day_max_usable_time), 0),
                max_study_time=Coalesce(Subquery(day_max_study_time), 0),
                max_time_usage_ratio=Coalesce(Subquery(day_max_time_usage_ratio), Decimal(0)),
            )\
            .order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Enables post requests on the server.

        Note: post request is not cached, so it can be used to refresh cache.
        """

        if self.request.body.decode() == 'refresh':
            # Clear cache
            cache_key = make_template_fragment_key('stage_list', [self.request.user.username])
            # cache_key = get_cache_key(self.request, 'list_stage', 'GET')
            caches['default'].delete(cache_key)

        # Refresh by redirecting to current page
        return redirect(reverse('classic_tracker:list_stage'))


class StageUpdateView(LoginRequiredMixin, UpdateView):
    model = Stage
    form_class = StageCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form
        kwargs['user'] = self.request.user
        return kwargs


class StageDeleteView(LoginRequiredMixin, DeleteView):
    model = Stage
    success_url = reverse_lazy('thank_you')


class StageDetailView(LoginRequiredMixin, DetailView):
    model = Stage

    # Extra context variables to display
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stage = self.get_object()

        items_per_page = 2
        page = int(self.request.GET.get('page', default=1))
        offset = items_per_page * (page - 1)
        days = Day.objects.filter(stage=stage)
        context['total_nb_pages'] = max(1, ceil(days.count() / items_per_page))
        days = days.order_by('-id')[offset:offset+items_per_page]
        context['days'] = days

        # Unit conversion
        context['total_usable_time'] = seconds_to_hours_minutes(stage.total_usable_time)
        context['total_study_time'] = seconds_to_hours_minutes(stage.total_study_time)
        context['total_work_time'] = seconds_to_hours_minutes(stage.total_work_time)
        context['time_usage_percentage'] = round(stage.time_usage_ratio * 100, 2)

        if days:
            context['max_usable_time'] \
                = seconds_to_hours_minutes(days.aggregate(Max('usable_time'))['usable_time__max'])
            context['max_study_time'] = seconds_to_hours_minutes(days.aggregate(Max('study_time'))['study_time__max'])
            context['max_time_usage_percentage'] \
                = round(context['days'].aggregate(Max('time_usage_ratio'))['time_usage_ratio__max'] * 100, 2)
        else:
            context['max_usable_time'] = 0
            context['max_study_time'] = 0
            context['max_time_usage_percentage'] = 0

        try:
            context['avg_usable_time'] = seconds_to_hours_minutes(stage.total_usable_time // stage.day_count)
        except ZeroDivisionError:
            context['avg_usable_time'] = 0

        try:
            context['avg_study_time'] = seconds_to_hours_minutes(stage.total_study_time // stage.day_count)
        except ZeroDivisionError:
            context['avg_study_time'] = 0

        try:
            context['avg_session_per_day'] = round(stage.session_count / stage.day_count, 1)
        except ZeroDivisionError:
            context['avg_session_per_day'] = 0

        try:
            context['avg_session_time'] \
                = seconds_to_hours_minutes(stage.total_study_time // stage.session_count)
        except ZeroDivisionError:
            context['avg_session_time'] = 0

        return context


class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def form_valid(self, form):
        # Get subject object
        obj = form.save(commit=False)

        # Automatically fill the user field
        # Note: obj will be saved later when super().form_valid(form) is called
        obj.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form
        kwargs['user'] = self.request.user
        return kwargs


class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    # Customize the name of the object_list sent to template
    context_object_name = 'subject_list'

    def get_queryset(self):

        # Only list subjects of the current user
        # Default ordering is by time of creation (last created <-> on the top)
        return Subject.objects.filter(user=self.request.user.id).order_by('-id')

    def post(self, request, *args, **kwargs):
        """
        Enables post requests on the server.

        Note: post request is not cached, so it can be used to refresh cache.
        """

        if self.request.body.decode() == 'refresh':
            # Clear cache
            cache_key = make_template_fragment_key('subject_list', [self.request.user.username])
            # cache_key = get_cache_key(self.request, 'list_subject', 'GET')
            caches['default'].delete(cache_key)

        # Refresh by redirecting to current page
        return redirect(reverse('classic_tracker:list_subject'))


class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectCreateUpdateForm
    success_url = reverse_lazy('thank_you')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass current user to form
        kwargs['user'] = self.request.user
        return kwargs


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy('thank_you')


class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject

    # Extra context variables to display
    def get_context_data(self, **kwargs):
        subject_obj = self.get_object()
        context = super().get_context_data(**kwargs)
        context['sessions'] = Session.objects.filter(subject=subject_obj)

        # Conversion from seconds to hours minutes
        context['total_study_time'] = seconds_to_hours_minutes(subject_obj.total_study_time)
        try:
            context['avg_session_time'] = seconds_to_hours_minutes(
                subject_obj.total_study_time / subject_obj.session_count)
        except ZeroDivisionError:
            context['avg_session_time'] = 0

        return context
