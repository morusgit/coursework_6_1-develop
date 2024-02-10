import calendar
from datetime import timedelta, datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import inlineformset_factory
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import MailingSettingsForm, MessageForm
from .models import MailingSettings, MailingLog, Message


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    extra_context = {
        'title': 'Создать сообщение'
    }

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('distribution:message_list')


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    extra_context = {
        'title': 'Редактировать сообщение'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.filter(groups__name='manager').exists():
                raise Http404
        return self.object

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('distribution:message_view', args=[self.object.pk])


class MessageListView(LoginRequiredMixin, ListView):
    model = Message

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:  # для работников и суперпользователя
            queryset = super().get_queryset()
        else:  # для остальных пользователей
            queryset = super().get_queryset().filter(owner=user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Список Сообщений'
        return context_data


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        message = self.get_object()
        context_data['title'] = message.title[:20]
        return context_data


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('distribution:message_list')
    extra_context = {
        'title': 'Удалить сообщение'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.filter(groups__name='manager').exists():
                raise Http404
        return self.object


class MailingSettingsCreateView(LoginRequiredMixin, CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    extra_context = {
        'title': 'Создать рассылку'
    }

    def get_initial(self):
        initial = super().get_initial()
        initial['owner'] = self.request.user
        return initial

    def form_valid(self, form):
        current_time = timezone.localtime(timezone.now())
        new_mailing = form.save()
        new_mailing.save()
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        if form.is_valid():
            clients = form.cleaned_data['clients']
            new_mailing = form.save()
            if new_mailing.start_time > current_time:
                new_mailing.next_send = new_mailing.start_time
            else:
                if new_mailing.periodicity == "Раз в день":
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=1)

                if new_mailing.periodicity == "Раз в неделю":
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=7)

                if new_mailing.periodicity == "Раз в месяц":
                    today = datetime.today()
                    days = calendar.monthrange(today.year, today.month)[1]
                    new_mailing.next_send = current_time + timedelta(days=days)

                for client in clients:
                    new_mailing.clients.add(client.pk)
                new_mailing.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('distribution:list')


class MailingSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    extra_context = {
        'title': 'Редактировать рассылку'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.filter(groups__name='manager').exists():
                raise Http404
        return self.object

    def get_initial(self):
        initial = super().get_initial()
        initial['owner'] = self.request.user
        return initial

    def form_valid(self, form):
        current_time = timezone.localtime(timezone.now())
        new_mailing = form.save()
        new_mailing.save()
        self.object = form.save()
        self.object.save()
        if form.is_valid():
            clients = form.cleaned_data['clients']
            new_mailing = form.save()
            if new_mailing.start_time > current_time:
                new_mailing.next_send = new_mailing.start_time
            else:
                if new_mailing.periodicity == "Раз в день":
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=1)

                if new_mailing.periodicity == "Раз в неделю":
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=7)

                if new_mailing.periodicity == "Раз в месяц":
                    today = datetime.today()
                    days = calendar.monthrange(today.year, today.month)[1]
                    new_mailing.next_send = new_mailing.start_time + timedelta(days=days)

                for client in clients:
                    new_mailing.clients.add(client.pk)
                new_mailing.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('distribution:view', args=[self.object.pk])


class MailingSettingsListView(LoginRequiredMixin, ListView):
    model = MailingSettings

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:  # для работников и суперпользователя
            queryset = super().get_queryset()
        else:  # для остальных пользователей
            queryset = super().get_queryset().filter(owner=user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Список рассылок'

        context_data['all'] = context_data['object_list'].count()
        context_data['active'] = context_data['object_list'].filter(status=MailingSettings.STARTED).count()
        context_data['completed'] = context_data['object_list'].filter(status=MailingSettings.COMPLETED).count()

        return context_data


def toggle_active(request, pk):
    if request.user.is_staff:
        distribution = MailingSettings.objects.get(pk=pk)
        distribution.is_active = not distribution.is_active
        distribution.save()
        return redirect('distribution:list')


class MailingSettingsDetailView(LoginRequiredMixin, DetailView):
    model = MailingSettings

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = f'Детали рассылки:'
        return context_data


class MailingSettingsDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingSettings

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.filter(groups__name='manager').exists():
                raise Http404
        return self.object

    def get_success_url(self):
        return reverse('distribution:list')


class LogListView(LoginRequiredMixin, ListView):
    model = MailingLog

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:  # для работников и суперпользователя
            queryset = super().get_queryset()
        else:  # для остальных пользователей
            queryset = super().get_queryset().filter(owner=user)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['title'] = 'Список логов'

        context_data['all'] = context_data['object_list'].count()
        context_data['success'] = context_data['object_list'].filter(status=True).count()
        context_data['error'] = context_data['object_list'].filter(status=False).count()

        return context_data


class LogDetailView(LoginRequiredMixin, DetailView):
    model = MailingLog

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        log = self.get_object()
        context_data['title'] = f'log: {log.pk}'
        return context_data


class LogDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingLog
    success_url = reverse_lazy('distribution:log_list')
    extra_context = {
        'title': 'Удалить лог',
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if not self.request.user.is_superuser:
            if self.object.owner != self.request.user or self.request.user.filter(groups__name='manager').exists():
                raise Http404
        return self.object
