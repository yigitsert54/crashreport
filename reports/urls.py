from django.urls import path
from . import views


urlpatterns = [
    path('', views.reports_home, name="reports_home"),
    path('create-report-initial/', views.create_report_initial, name="create_report_initial"),
    path('edit-report/<str:report_id>/', views.edit_report_form, name="edit_report_form"),

]
