"""
DEPRECATED: Django CMS configuration for parodynews.

Django CMS integration has been removed as of 2025-11-25.
This file is kept for reference but should not be used.

TODO: Remove this file once CMS migration is complete.
"""

from cms.app_base import CMSApp, CMSAppConfig
from cms.apphook_pool import apphook_pool


class ParodyNewsCMSConfig(CMSAppConfig):
    name = "parodynews"
    verbose_name = "Parody News"

    def ready(self):
        apphook_pool.register(ParodyNewsApphook)


class ParodyNewsApphook(CMSApp):
    app_name = "parodynews"
    name = "Parody News Apphook"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["parodynews.urls"]


apphook_pool.register(ParodyNewsApphook)
