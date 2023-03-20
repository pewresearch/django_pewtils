import os
from django.apps import AppConfig

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class TestAppInstalledConfig(AppConfig):

    name = "testapp_installed"

    def update_settings(self):
        from django.conf import settings

        for setting, path in [("TEST_SETTINGS_FOLDERS", "testapp_installed")]:
            if hasattr(settings, setting):
                dirs = getattr(settings, setting)
            else:
                dirs = []
            dirs.append(path)
            dirs = list(set(dirs))
            setattr(settings, setting, dirs)

    def __init__(self, *args, **kwargs):
        super(TestAppInstalledConfig, self).__init__(*args, **kwargs)
        self.update_settings()

    def ready(self):
        self.update_settings()
