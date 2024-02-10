from django.db import models

from config import settings

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    """
    Модель клиента содержащая email и инфу клиента
    """
    email = models.EmailField(verbose_name='Email')
    name = models.CharField(max_length=64, verbose_name='Имя')
    surname = models.CharField(max_length=64, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=64, **NULLABLE, verbose_name='Отчество')
    comment = models.TextField(**NULLABLE, default=None, verbose_name='Комментарий')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Владелец', **NULLABLE)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('surname', 'name',)
