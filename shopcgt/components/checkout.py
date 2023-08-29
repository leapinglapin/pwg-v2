import os

import stripe
from dotenv import load_dotenv
from shopcgt.components.ProjectPaths import ProjectPaths

load_dotenv(os.path.join(ProjectPaths.BASE_DIR, '.env'))

CART_COOKIE_OPEN = "cgt_cart_open"
CART_COOKIE_LIFETIME = 604800

# SECURITY WARNING: keep the secret key used in production secret!
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")

stripe.api_key = STRIPE_SECRET_KEY

PAYPAL_ENDPOINT = os.getenv("PAYPAL_ENDPOINT")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

TAXJAR_API_KEY = os.getenv("TAXJAR_API_KEY")

QUADERNO_PRIVATE = os.getenv("QUADERNO_PRIVATE")
QUADERNO_PUBLIC = os.getenv("QUADERNO_PUBLIC")
QUADERNO_URL = os.getenv("QUADERNO_URL")

CORS_ALLOWED_ORIGINS = ["https://3.18.12.63",
                        "https://3.130.192.231",
                        "https://13.235.14.237",
                        "https://13.235.122.149",
                        "https://35.154.171.200",
                        "https://52.15.183.38",
                        "https://54.187.174.169",
                        "https://54.187.205.235",
                        "https://54.187.216.72",
                        "https://54.241.31.99",
                        "https://54.241.31.102",
                        "https://54.241.34.107"]
