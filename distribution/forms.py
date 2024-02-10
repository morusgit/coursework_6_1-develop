from django.forms import ModelForm

from clients.models import Client
from distribution.models import Message, MailingSettings


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class MailingSettingsForm(StyleFormMixin, ModelForm):
    class Meta:
        model = MailingSettings
        fields = ('start_time', 'end_time', 'periodicity', 'clients', 'message',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        owner = kwargs.pop('initial').get('owner')
        if not owner.is_superuser:
            self.fields['clients'].queryset = Client.objects.all().filter(owner=owner)
            self.fields['message'].queryset = Message.objects.all().filter(owner=owner)


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ('title', 'text',)
