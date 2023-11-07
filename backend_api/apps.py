from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class BackendApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend_api'

    def ready(self):
        """
        импортируем сигналы
        """
        required_mw = "allauth.account.middleware.AccountMiddleware"
        if required_mw not in settings.MIDDLEWARE:
            raise ImproperlyConfigured(
                f"{required_mw} должен быть добавлен в settings.MIDDLEWARE"
            )