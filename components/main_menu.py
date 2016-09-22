from __future__ import print_function, unicode_literals

from django.contrib.auth import logout
from django.utils.translation import ugettext_lazy as _

from cba import components


class MainMenu(components.Menu):
    def init_components(self):
        self.initial_components = [
            components.MenuItem(name="Logout", handler="handle_logout"),
            components.MenuItem(name="Test", href="/test.de", default_ajax=False),
            components.MenuItem(id="about-us", name="About us", handler="handle_about_us"),
        ]

    def handle_about_us(self):
        root = self.get_root()
        root.add_component(
            components.Modal(
                id="modal-1",
                header="About us",
                initial_components=[
                    components.Text(
                        value="""Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.""")
                ]),
        )
        root.refresh()

    def handle_logout(self):
        request = self.get_request()
        logout(request)

        root = self.get_root()
        root.refresh_all()
        root.add_message(_("You are logged out!"), "success")
