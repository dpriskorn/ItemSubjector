from wikibaseintegrator import wbi_config, wbi_login

import config


class Login:
    def __init__(self):
        self.login()

    @staticmethod
    def login():
        from src.helpers.console import console

        with console.status("Logging in with WikibaseIntegrator..."):
            config.login_instance = wbi_login.Login(
                user=config.username,
                password=config.password,
            )
            # Set User-Agent
            wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent
