from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.reports_home, name="reports_home"),
    path('create-report/', views.DamageReportWizardView.as_view(views.DAMAGE_REPORT_FORMS), name="create_report"),
    path('create-report-initial/', views.create_report_initial, name="create_report_initial"),
    path('edit-report/<str:report_id>/', views.edit_report_form, name="edit_report_form"),

]
