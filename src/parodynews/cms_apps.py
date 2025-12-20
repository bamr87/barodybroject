"""
DEPRECATED: Django CMS app configuration for parodynews.

Django CMS integration has been removed as of 2025-11-25.
This file is kept for reference but should not be used.

TODO: Remove this file once CMS migration is complete.
"""

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


@apphook_pool.register
class PostPageConfig(CMSApp):
    app_name = "parodynews"
    name = "Post Page Config"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["parodynews.urls"]

    def get_configs(self):
        return self.app_config.objects.all()

    def get_config(self, namespace):
        try:
            return self.app_config.objects.get(namespace=namespace)
        except ObjectDoesNotExist:
            return None

    def get_config_add_url(self):
        try:
            return reverse(
                f"admin:{self.app_config._meta.app_label}_{self.app_config._meta.model_name}_add"
            )
        except AttributeError:
            return reverse(
                f"admin:{self.app_config._meta.app_label}_{self.app_config._meta.module_name}_add"
            )
