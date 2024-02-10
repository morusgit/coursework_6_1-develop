from django.db import models

from clients.models import Client
from config import settings

NULLABLE = {'blank': True, 'null': True}


class Message(models.Model):
    title = models.CharField(max_length=100, verbose_name='Тема письма')
    text = models.TextField(verbose_name='Письмо')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Владелец', **NULLABLE)

    def __str__(self):
        return f'message title:{self.title}'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ('title',)


class MailingSettings(models.Model):
    DAILY = "Раз в день"
    WEEKLY = "Раз в неделю"
    MONTHLY = "Раз в месяц"

    PERIODICITY_CHOICES = [
        (DAILY, "Раз в день"),
        (WEEKLY, "Раз в неделю"),
        (MONTHLY, "Раз в месяц"),
    ]

    CREATED = 'Создана'
    STARTED = 'Запущена'
    COMPLETED = 'Завершена'

    STATUS_CHOICES = [
        (COMPLETED, "Завершена"),
        (CREATED, "Создана"),
        (STARTED, "Запущена"),
    ]

    ACTIVE_CHOICES = ((True, 'Активна'), (False, 'На модерации'))

    start_time = models.DateTimeField(verbose_name='Дата начала рассылки')
    end_time = models.DateTimeField(verbose_name='Дата окончания рассылки')
    next_send = models.DateTimeField(**NULLABLE, verbose_name='Дата следующей рассылки')
    periodicity = models.CharField(choices=PERIODICITY_CHOICES, max_length=50, verbose_name='Периодичность')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=CREATED, verbose_name='Статус рассылки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, default=None, verbose_name='Сообщение')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты рассылки')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Владелец', **NULLABLE)
    is_active = models.BooleanField(default=True, choices=ACTIVE_CHOICES, verbose_name='Активна')

    def __str__(self):
        return f'time: {self.start_time} - {self.end_time}, periodicity: {self.periodicity}, status: {self.status}'

    class Meta:
        verbose_name = 'настройки рассылки'
        verbose_name_plural = 'настройки рассылки'
        ordering = ('created_at',)


class MailingLog(models.Model):
    time = models.DateTimeField(verbose_name='Дата и время создания лога', auto_now_add=True)
    status = models.BooleanField(verbose_name='Статус попытки')
    server_response = models.CharField(max_length=1000, verbose_name='Ответ почтового сервера', **NULLABLE)
    mailing = models.ForeignKey(MailingSettings, on_delete=models.CASCADE, verbose_name='Рассылка')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, **NULLABLE, on_delete=models.SET_NULL, verbose_name='Владелец')

    def __str__(self):
        return f'{self.time} {self.status}'

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'
        ordering = ('time',)
