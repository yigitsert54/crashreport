from django.contrib import admin


def sorted_verbose_name(position: int, database_display_name: str) -> str:
    """
    Returns the database sorted name for better display in the database.

    :param position: Position in which the model should be displayed in the database
    :param database_display_name: verbose name of the model in the database

    :return: Sorted database name (with starting spaces)
    """

    def decorator(cls):

        spaces = " " * 100  # Erzeuge 100 Leerzeichen
        sorted_name = spaces.replace(" ", "", position) + database_display_name

        if hasattr(cls, '_meta'):
            cls._meta.verbose_name_plural = sorted_name
        return cls

    return decorator


def changelist_view(model_title=None):
    """
    Changes the view in the database. I can add a custom title to the data base view.
    + A Model description is added, which will be extracted from the model doc string.
    """

    def decorator(cls):
        # Hole die ursprüngliche changelist_view Methode
        original_changelist_view = getattr(cls, 'changelist_view', admin.ModelAdmin.changelist_view)

        def custom_changelist_view(self, request, extra_context=None):
            # Initialisiere extra_context, falls None
            if extra_context is None:
                extra_context = {}

            # Setze Titel
            if model_title is not None and model_title != "":
                extra_context['title'] = model_title
            else:
                extra_context['title'] = self.model._meta.verbose_name_plural.strip()

            # Prüfe Docstring
            doc_string_empty = bool(self.model.__name__ + "(" in self.model.__doc__)

            # Füge Beschreibung hinzu, wenn Docstring nicht leer
            if not doc_string_empty:
                extra_context['model_description'] = self.model.__doc__

            # Rufe ursprüngliche Methode auf
            return original_changelist_view(self, request, extra_context=extra_context)

        # Ersetze changelist_view Methode
        cls.changelist_view = custom_changelist_view
        return cls
    return decorator
