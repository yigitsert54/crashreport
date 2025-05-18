from django.urls import path
from . import views
from . import landingpages

urlpatterns = [
    path("", views.home, name="home"),
    path('register/', views.user_registration, name="register"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),

    # Settings
    path('settings/', views.settings, name="settings"),
    path('settings/change-password/', views.change_password, name="change_password"),
    path('settings/edit-account/', views.edit_account_data, name="edit_account_data"),
    path('settings/edit-workshop-data/', views.edit_workshop_data, name="edit_workshop_data"),

    # Landing pages
    path('dashboard/', views.dashboard, name="dashboard"),
    path('uikit/', views.uikit, name="uikit"),
    path('landing-1', landingpages.landing_1, name="landing_1"),
    path('landing-2', landingpages.landing_2, name="landing_2"),
]
