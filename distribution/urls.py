from django.urls import path
from distribution.apps import DistributionConfig
from distribution.views import MessageListView, MessageCreateView, MessageUpdateView, MessageDetailView, \
    MessageDeleteView, MailingSettingsListView, MailingSettingsDetailView, \
    MailingSettingsDeleteView, LogListView, LogDetailView, LogDeleteView, MailingSettingsCreateView, \
    MailingSettingsUpdateView, toggle_active

app_name = DistributionConfig.name

urlpatterns = [
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('message_create/', MessageCreateView.as_view(), name='message_create'),
    path('message_edit/<int:pk>/', MessageUpdateView.as_view(), name='message_edit'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_view'),
    path('message_delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),

    path('list/', MailingSettingsListView.as_view(), name='list'),
    path('toggle-active/<int:pk>/', toggle_active, name='toggle_active'),
    path('view/<int:pk>/', MailingSettingsDetailView.as_view(), name='view'),
    path('create/', MailingSettingsCreateView.as_view(), name='create'),
    path('edit/<int:pk>/', MailingSettingsUpdateView.as_view(), name='edit'),
    path('delete/<int:pk>/', MailingSettingsDeleteView.as_view(), name='delete'),

    path('logs', LogListView.as_view(), name='log_list'),
    path('log/<int:pk>/', LogDetailView.as_view(), name='log_detail'),
    path('log_delete/<int:pk>/', LogDeleteView.as_view(), name='log_delete'),
]
