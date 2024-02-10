import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetDoneView
from django.core.cache import cache

from django.core.mail import send_mail
from django.http import Http404
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, UpdateView, TemplateView, ListView
from django.urls import reverse_lazy, reverse
from django.core.cache import cache
from blog.models import Post
from clients.models import Client
from config import settings
from distribution.models import MailingSettings
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User
from django.shortcuts import redirect, render
from django.contrib.auth import login


class MainPage(LoginRequiredMixin, TemplateView):
    login_url = 'users:login'
    template_name = 'users/main.html'
    extra_context = {
        'title': 'Сайт отправки рассылок'
    }

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        if self.request.method == 'GET':
            if settings.CACHE_ENABLED:
                key = f'cached_statistics'
                cached_context = cache.get(key)
                if cached_context is None:
                    context = super().get_context_data(*args, **kwargs)
                    if not user.is_staff:
                        context['mailing_count'] = MailingSettings.objects.filter(owner=user).count()
                        context['enabled_mailing'] = MailingSettings.objects.filter(owner=user).filter(
                            status='Запущена').count()
                        unic_client = []
                        for client in Client.objects.filter(owner=user):
                              unic_client.append(client.email)
                        context['unique_clients'] = len(set(unic_client))
                        all_blog_posts = Post.objects.all()
                        random.shuffle(list(all_blog_posts))
                        context['three_random_posts'] = all_blog_posts[:3]
                    else:
                        context['mailing_count'] = MailingSettings.objects.all().count()
                        context['enabled_mailing'] = MailingSettings.objects.all().filter(status='Запущена').count()
                        unic_client = []
                        for client in Client.objects.all():
                            unic_client.append(client.email)
                        context['unique_clients'] = len(set(unic_client))
                        main_page_context = {
                            'mailing_count': context['mailing_count'],
                            'enabled_mailing': context['enabled_mailing'],
                            'unique_clients': context['unique_clients']
                        }
                        cache.set(key, main_page_context)
                        all_blog_posts = Post.objects.all()
                        random.shuffle(list(all_blog_posts))
                        context['three_random_posts'] = all_blog_posts[:3]
                    return context
                else:
                    context = super().get_context_data(*args, **kwargs)
                    context['mailing_count'] = cached_context['mailing_count']
                    context['enabled_mailing'] = cached_context['enabled_mailing']
                    context['unique_clients'] = cached_context['unique_clients']
                    all_blog_posts = Post.objects.all()
                    random.shuffle(list(all_blog_posts))
                    context['three_random_posts'] = all_blog_posts[:3]
                return context


class RegisterView(CreateView):
    """ Регистрация нового пользователя и его валидация через письмо на email пользователя """
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()

        # формируем токен и ссылку для подтверждения регистрации
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = reverse_lazy('users:confirm_email', kwargs={'uidb64': uid, 'token': token})

        current_site = '127.0.0.1:8000'

        send_mail(
            subject='Регистрация на платформе',
            message=f"Завершите регистрацию, перейдя по ссылке: http://{current_site}{activation_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return redirect('users:email_confirmation_sent')


class UserConfirmationSentView(PasswordResetDoneView):
    """ Выводит информацию об отправке на почту подтверждения регистрации """
    template_name = "users/registration_sent_done.html"
    extra_context = {
        'title': 'На почту отправлена ссылка подтверждения регистрации'
    }


class UserConfirmEmailView(View):
    """ Подтверждение пользователем регистрации """

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('users:email_confirmed')
        else:
            return redirect('users:email_confirmation_failed')


class UserConfirmedView(TemplateView):
    """ Выводит информацию об успешной регистрации пользователя """
    template_name = 'users/registration_confirmed.html'


class UserConfirmationFailView(View):
    """ Выводит информацию о невозможности зарегистрировать пользователя """
    template_name = 'users/email_confirmation_failed.html'


class UserUpdateView(UpdateView, LoginRequiredMixin):
    """ Контроллер профиля пользователя """
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        #""" Позволяет делать необязательным передачу pk объекта но пользователи не могут завести свой профиль """
        #if not self.request.user.is_superuser:
        #    if self.object.owner != self.request.user or self.request.user.filter(groups__name='manager').exists():
        #        raise Http404
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование профиля'
        return context


class UserListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = User
    permission_required = 'users.view_user'  # Указание правила доступа к контроллеру
    extra_context = {
        'title': 'Список пользователей'
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:  # для суперпользователя
            queryset = super().get_queryset()
        elif user.is_staff:
            queryset = super().get_queryset().filter(is_staff=False)
        else:  # для остальных пользователей
            queryset = None
        return queryset


def toggle_active(request, pk):
    if request.user.is_staff:
        user = User.objects.get(pk=pk)
        user.is_active = not user.is_active
        user.save()
        return redirect('users:user_list')


@login_required
def generate_new_password(request):
    """ Генерирует новый пароль пользователя """
    new_password = get_random_string(length=9)

    send_mail(
        subject='Новый пароль',
        message=f'Ваш новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email]
    )

    request.user.set_password(new_password)
    request.user.save()

    return redirect(reverse('users:main'))


def regenerate_password(request):
    """ Генерирует новый пароль пользователя """
    if request.method == 'POST':
        email = request.POST.get('email')
        # Получаем пользователя по email
        user = User.objects.get(email=email)

        # Генерируем новый пароль
        new_password = get_random_string(length=9)

        # Изменяем пароль пользователя
        user.set_password(new_password)
        user.save()

        # Отправляем письмо с новым паролем
        send_mail(
            subject='Восстановление пароля',
            message=f'Ваш новый пароль: {new_password}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return redirect(reverse('users:main'))
    return render(request, 'users/regenerate_password.html')
