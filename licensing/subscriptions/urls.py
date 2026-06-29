from django.urls import path
from .views import PlanListView, SubscriptionCheckView, ProcessSubscriptionView, CancelSubscriptionView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='subscriptions.plans'),
    path('check/', SubscriptionCheckView.as_view(), name='subscriptions.check'),
    path('process/', ProcessSubscriptionView.as_view(), name='subscriptions.process'),
    path('cancel/', CancelSubscriptionView.as_view(), name='subscriptions.cancel'),
]
