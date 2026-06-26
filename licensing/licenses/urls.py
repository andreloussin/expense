from django.urls import path

from .views import (
    ActivateView,
    CreateLicenseView,
    LicenseListView,
    LicenseDetailView,
    RevokeMachineView,
    ReactivateMachineView,
    LicenseStatusView,
    MachineStatusView
)

urlpatterns = [
    # creation
    path("create/", CreateLicenseView.as_view()),
    path("status/", LicenseStatusView.as_view()),
    
    
    # activation
    path("activate/", ActivateView.as_view()),

    # licenses
    path("", LicenseListView.as_view()),
    path("<uuid:pk>/", LicenseDetailView.as_view()),

    # machine control
    path("<uuid:pk>/machines/<str:machine_id>/revoke/", RevokeMachineView.as_view()),
    path("<uuid:pk>/machines/<str:machine_id>/reactivate/", ReactivateMachineView.as_view()),
    path("<uuid:pk>/machines/<str:machine_id>/status/", MachineStatusView.as_view()),
]