"""
DEPRECATED: Django CMS menus for parodynews.

Django CMS integration has been removed as of 2025-11-25.
This file is kept for reference but should not be used.

TODO: Remove this file once CMS migration is complete.
"""

from cms.menu_bases import CMSAttachMenu
from django.utils.translation import gettext_lazy as _
from menus.base import NavigationNode
from menus.menu_pool import menu_pool


class MyCustomMenu(CMSAttachMenu):
    name = _("My Custom Menu")  # This name will appear in the admin interface

    def get_nodes(self, request):
        nodes = []
        # Add your menu items here
        n = NavigationNode(_("Sample Item"), "/sample-url/", 1)
        nodes.append(n)
        return nodes


menu_pool.register_menu(MyCustomMenu)
