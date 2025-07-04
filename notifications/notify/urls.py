from django.urls import path
from .views import CreateNotificationView, NotificationDeleteView, MarkAsRead, NotificationListView

urlpatterns = [
    path('notifications/<int:pk>/read/', MarkAsRead.as_view(), name='mark-as-read'),
    path('notifications/create/', CreateNotificationView.as_view(), name='create-notification'),
    path('notifications/list/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/delete/<int:pk>/', NotificationDeleteView.as_view(), name='notification-delete'),
]