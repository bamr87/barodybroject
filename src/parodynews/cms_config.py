from cms.app_base import CMSAppConfig
from cms.apphook_pool import apphook_pool

class ParodyNewsCMSConfig(CMSAppConfig):
    name = "parodynews"
    verbose_name = "Parody News"

    def ready(self):
        apphook_pool.register(ParodyNewsApphook)

from cms.app_base import CMSApp

class ParodyNewsApphook(CMSApp):
    app_name = "parodynews"
    name = "Parody News Apphook"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["parodynews.urls"]

apphook_pool.register(ParodyNewsApphook)