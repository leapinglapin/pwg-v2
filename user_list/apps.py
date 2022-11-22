from django.apps import AppConfig


class UserListConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_list'

    def ready(self):
        # Implicitly connect a signal handlers decorated with @receiver.
        from . import signals
