from __future__ import print_function, unicode_literals

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _

from cba import components


class Login(components.Group):
    def init_components(self):
        self.initial_components = [
            components.Group(
                css_class="ui container form",
                attributes={"style": "margin-top: 200px; width: 400px"},
                initial_components=[
                    components.HTML(
                        tag="h2",
                        attributes={"style": "text-align:center"},
                        text=_("Please log in!"),
                    ),
                    components.Group(
                        id="login-form",
                        css_class="ui stacked segment",
                        initial_components=[
                            components.TextInput(
                                id="username",
                                icon="user",
                                placeholder=_("Username")
                            ),
                            components.TextInput(
                                id="password",
                                icon="lock",
                                placeholder=_("Password")
                            ),
                            components.Button(
                                id="login",
                                value="Login",
                                handler={"click": "server:handle_login"},
                                css_class="primary fluid"
                            ),
                        ],
                    ),
                ]
            ),
        ]

    def handle_login(self):
        username = self.get_component("username").value
        password = self.get_component("password").value
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(self.get_request(), user)
                root = self.get_root()
                root.refresh_all()
                root.add_message(_("You are logged in!"), "success")
            else:
                self.add_message(_("Your account is not acitve!"), "error")
        else:
            self.add_message(_("Username and password don't match!"), "error")
