from django.apps import AppConfig


class BookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "book"

    def ready(self):
        def import_signals():
            import book.signals

        import_signals()