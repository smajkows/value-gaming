import os

# Sandbox Braintree account credentials to use as defaults for local development
SANDBOX_BT_ENVIRONMENT = 'sandbox'
SANDBOX_BT_MERCHANT_ID = 'ntydjmbm732drtxb'
SANDBOX_BT_PUBLIC_KEY = 'hgttdgm643s5krp9'
SANDBOX_BT_PRIVATE_KEY = 'dfe284a583da583ac943a986001f7b70'


def get_logging_credentials():
    env = os.getenv("PROJECT_NAME", None)
    credential_file_string = 'app_engine_credentials/{}_python3logging.json'.format(env)
    return credential_file_string


def get_stats_domain():
    domain = os.getenv("STATS_DOMAIN", None)
    if not domain:
        domain = 'http://localhost:8000'
    return domain


def get_braintree_env_variables():
    return os.getenv("BT_ENVIRONMENT", SANDBOX_BT_ENVIRONMENT), os.getenv("BT_MERCHANT_ID", SANDBOX_BT_MERCHANT_ID),\
           os.getenv("BT_PUBLIC_KEY", SANDBOX_BT_PUBLIC_KEY), os.getenv("BT_PRIVATE_KEY", SANDBOX_BT_PRIVATE_KEY)
