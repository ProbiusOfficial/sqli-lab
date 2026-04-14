import os


class Config:
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "sqli_app")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "sqli_app_change_me")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "sqli_lab")
    MYSQL_ADMIN_USER = os.environ.get("MYSQL_ADMIN_USER", "sqli_admin")
    MYSQL_ADMIN_PASSWORD = os.environ.get("MYSQL_ADMIN_PASSWORD", "sqli_admin_change_me")
    RESET_TOKEN = os.environ.get("RESET_TOKEN", "")
    MYSQL_ROOT_PASSWORD = os.environ.get("MYSQL_ROOT_PASSWORD", "root_change_me")
