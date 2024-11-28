from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from .models import PostPluginModel

@plugin_pool.register_plugin
class PostPlugin(CMSPluginBase):
    model = PostPluginModel
    name = _("Post Plugin")
    render_template = "parodynews/cms.html"
    cache = False

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        context['post'] = instance.post
        return context