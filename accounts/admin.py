from django.contrib import admin
from x_custom_decorators import changelist_view

# import models
from .models import (
    Account,
    WorkshopData
)


@changelist_view(model_title="Accountübersicht")
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list.html'

    # Admin list settings
    list_display = ['name_display', 'email', 'user']
    # readonly_fields = []
    # list_filter = []
    # list_editable = []
    list_display_links = ['name_display', 'email']
    search_fields = ('first_name', 'last_name', 'email')

    @admin.display(ordering='first_name', description='Name')
    def name_display(self, obj):

        if obj.first_name:
            first_name = obj.first_name
        else:
            first_name = "Vorname"

        if obj.last_name:
            last_name = obj.last_name
        else:
            last_name = "Nachname"

        return f"{first_name} {last_name}"


@changelist_view(model_title="")
@admin.register(WorkshopData)
class WorkshopDataAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list.html'

    # Admin list settings
    list_display = ['name_display', 'account_display', 'address_display', "contact_display"]
    # readonly_fields = []
    # list_filter = []
    # list_editable = []
    # list_display_links = []
    search_fields = (
        'account__first_name',
        'account__last_name',
        'account__email',
        'workshop_name',
        'primary_contact'
    )

    @admin.display(ordering='workshop_name', description='Werkstatt')
    def name_display(self, obj):

        if obj.workshop_name:
            return obj.workshop_name
        else:
            return "-"

    @admin.display(ordering='account', description='Account')  # Ordnet nach dem Modell-Feld `data_source`
    def account_display(self, obj):

        if obj.account.first_name:
            first_name = obj.account.first_name
        else:
            first_name = "Vorname"

        if obj.account.last_name:
            last_name = obj.account.last_name
        else:
            last_name = "Nachname"

        return f"{first_name} {last_name} - {obj.account.email}"

    @admin.display(ordering='plz', description='Adresse')
    def address_display(self, obj):

        address_string = ""

        if obj.address:
            address_string += obj.address + " "

        if obj.plz:
            address_string += obj.plz + " "

        if obj.city:
            address_string += obj.city + " "

        if len(address_string) > 0:
            return address_string.strip()
        else:
            return "-"

    @admin.display(ordering='primary_contact', description='Kontaktperson')
    def contact_display(self, obj):

        if obj.primary_contact:
            return obj.primary_contact
        else:
            return "-"
