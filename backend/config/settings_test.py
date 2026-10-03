from .settings import *  # noqa: F403

# Django's default PBKDF2 hasher is deliberately slow; tests don't need that.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Tests must not call OpenAI or Stripe: mock those calls in the test. Blank keys make
# a forgotten mock fail instead of using the real keys from the Docker container's .env.
OPENAI_API_KEY = ''
STRIPE_SECRET_KEY = ''
