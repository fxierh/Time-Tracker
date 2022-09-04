import os
import subprocess

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import TemplateView, FormView, UpdateView

from . import settings
from .forms import RegistrationForm, PasswordResetFormExtended, UserUpdateForm
from .settings import BASE_DIR
from classic_tracker.models import User


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: write test

        # Count number of lines of code
        args_count_lines = [os.path.join(BASE_DIR, 'time_tracker/count_lines_of_code.sh'), BASE_DIR]
        frontend_line_count, backend_line_count, test_line_count \
            = subprocess.check_output(args_count_lines).decode().strip().split('\n')

        # Count test cases
        args_count_test = [os.path.join(BASE_DIR, 'time_tracker/count_test_cases.sh'), BASE_DIR]
        test_case_count = subprocess.check_output(args_count_test).decode().strip()

        context['frontend_line_count'] = frontend_line_count
        context['backend_line_count'] = backend_line_count
        context['test_line_count'] = test_line_count
        context['test_case_count'] = test_case_count
        return context


class NotFoundView(TemplateView):
    template_name = '404.html'


class ThankYouView(TemplateView):
    template_name = 'thank_you.html'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user_update.html'
    success_url = reverse_lazy('thank_you')


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('thank_you')

    def form_valid(self, form):
        form.save()

        # Log in user automatically after registration
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)

        # Send email
        # Note:
        # 1. The attributes (subject, message etc.) are assembled into a Django EmailMessage Object,
        # which is then passed to email_backend_class_name.send_messages([EmailMessage Objects]).
        # 2. For recipients with non-HTML email clients, the message argument is used.
        # For recipients with HTML email clients, the html_message argument will be used if specified,
        # otherwise the message argument is used.
        # 3. The send_email function below returns the number of EmailMessage sent.

        send_mail(
            subject='Registration to Time Tracker',
            message=f'Congrats {username}, your registration is successful !',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.request.POST['email']],
            # html_message='<h1> ... <h1>',
        )

        return super().form_valid(form)


class PasswordResetFormView(FormView):
    form_class = PasswordResetFormExtended
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        # Get user email and user
        email = self.request.POST['email']
        user = User.objects.get(email=email)

        # Context variable passed to the email
        context = {
            'email': email,
            'domain': settings.DOMAIN_NAME,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        }

        # Send email
        # Note:
        # 1. The attributes (subject, message etc.) are assembled into a Django EmailMessage Object,
        # which is then passed to email_backend_class_name.send_messages([EmailMessage Objects]).
        # 2. For recipients with non-HTML email clients, the message argument is used.
        # For recipients with HTML email clients, the html_message argument will be used if specified,
        # otherwise the message argument is used.
        # 3. The send_email function below returns the number of EmailMessage sent.

        send_mail(
            subject='Password Reset',
            message=render_to_string('password_reset_email.txt', context),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return super().form_valid(form)
