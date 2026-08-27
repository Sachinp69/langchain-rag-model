from supabase import create_client, ClientOptions
from app.core.config import settings

def get_user_supabase_client(token: str):
    options = ClientOptions(
        headers={"Authorization": f"Bearer {token}"}
    )
    client = create_client(settings.supabase_url, settings.supabase_key, options=options)
    return client