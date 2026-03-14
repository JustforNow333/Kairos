from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from .config import settings

# In production, these must be set in the .env file
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID or "mock-client-id",
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET or "mock-client-secret"
})

oauth = OAuth(config)

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile https://www.googleapis.com/auth/calendar.readonly"
    }
)
