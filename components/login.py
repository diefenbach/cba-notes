from __future__ import print_function, unicode_literals

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _

from cba import components
from cba import layouts


class Login(components.Group):
    def init_components(self):
        self.initial_components = [
            layouts.Grid(
                id="login-form",
                css_class="middle aligned center aligned",
                initial_components=[
                    layouts.Column(
                        initial_components=[
                            components.TextInput(
                                id="username",
                                label=_("Username")
                            ),
                            components.TextInput(
                                id="password",
                                label=_("Password")
                            ),
                            components.Button(
                                id="login",
                                value="Login",
                                handler="handle_login",
                                css_class="primary fluid"
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def handle_login(self):
        username = self.get_component("username").value
        password = self.get_component("password").value
        user = authenticate(username=username, password=password)

        request = self.get_request()

        if user is not None:
            if user.is_active:
                login(request, user)
                root = self.get_root()
                root.refresh_all()
                root.add_message(_("You are logged in!"), "success")
            else:
                self.add_message(_("Your account is not acitve!"), "error")
        else:
            self.add_message(_("Username and password don't match!"), "error")
