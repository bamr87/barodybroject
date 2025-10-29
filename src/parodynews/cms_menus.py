from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import gettext_lazy as _
from cms.menu_bases import CMSAttachMenu


class MyCustomMenu(CMSAttachMenu):
    name = _("My Custom Menu")  # This name will appear in the admin interface

    def get_nodes(self, request):
        nodes = []
        # Add your menu items here
        n = NavigationNode(_("Sample Item"), "/sample-url/", 1)
        nodes.append(n)
        return nodes


menu_pool.register_menu(MyCustomMenu)
