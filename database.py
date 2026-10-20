
import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@st.cache_resource
def get_supabase() -> Client:
    """Create a reusable Supabase client."""

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials are missing. Check your .env file."
        )

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def get_authenticated_supabase(access_token: str) -> Client:
    """Create a client authenticated as the current user."""

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials are missing. Check your .env file."
        )

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    client.postgrest.auth(access_token)

    return client
