from django import forms
from .models import Client


class StyleFormMixin:
    """
    Миксин форма со стилем форм
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ClientForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для модели клиента
    """

    class Meta:
        model = Client
        exclude = ('owner',)  # Использование всех полей, кроме перечисленных
