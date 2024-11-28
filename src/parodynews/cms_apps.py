from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


from .models import PostPageConfigModel


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
           return reverse("admin:{}_{}_add".format(self.app_config._meta.app_label, self.app_config._meta.model_name))
        except AttributeError:
            return reverse(
                "admin:{}_{}_add".format(self.app_config._meta.app_label, self.app_config._meta.module_name)
            )