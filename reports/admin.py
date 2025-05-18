from django.contrib import admin
from x_custom_decorators import changelist_view
from django.utils.safestring import mark_safe
from django import forms

# import models
from .models import (
    DamageReport,
    DamageImage,
    AccidentScenarioOption,
    Witness
)


class DamageImageInline(admin.TabularInline):  # oder StackedInline
    model = DamageImage  # Definiert welches Child-Model eingebunden wird
    extra = 0  # Anzahl der leeren Formulare, die initial angezeigt werden
    fields = ('image', 'image_view', 'image_preview')  # Legt fest welche Felder im Inline-Formular sichtbar sind
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):  # Vorschau-Methode
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
        return "-"
    image_preview.short_description = "Vorschau"


class WitnessInline(admin.TabularInline):  # Oder StackedInline
    model = Witness
    extra = 0  # Keine leeren Formulare initial anzeigen
    fields = ('first_name', 'last_name', 'address', 'phone_number')


@changelist_view(model_title="Schadensberichte")
@admin.register(DamageReport)
class DamageReportAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list.html'

    # Admin list settings
    list_display = ['name_display', 'date_display', 'workshop_display']
    # readonly_fields = []
    list_filter = ["workshop"]
    # list_editable = []
    list_display_links = ['name_display']
    search_fields = ('first_name', 'last_name', 'plate_number', "workshop", "workshop__account")
    inlines = [WitnessInline, DamageImageInline]

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

    @admin.display(ordering='accident_datetime', description='Unfalldatum')
    def date_display(self, obj):

        if obj.accident_datetime:
            return obj.accident_datetime
        else:
            return None

    @admin.display(ordering='workshop_display', description='Werkstatt')
    def workshop_display(self, obj):

        if obj.workshop:
            return obj.workshop
        else:
            return None

    class Media:
        css = {
            'all': (
                'css/admin_stylings/admin_reports.css',
            )
        }

    # Change Select field to radio selct boxes

    def formfield_for_manytomany(self, db_field, request, **kwargs):

        # Usage field
        if db_field.name == "accident_scenarios":
            kwargs['widget'] = forms.CheckboxSelectMultiple()

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@changelist_view(model_title="Unfallszenarien")
@admin.register(AccidentScenarioOption)
class AccidentScenarioOptionAdmin(admin.ModelAdmin):

    change_list_template = 'admin/change_list.html'
