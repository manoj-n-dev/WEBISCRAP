from fastapi import APIRouter
# C5: api_router no longer mounts auth/chat sub-routers.
# All routing is done explicitly in main.py to avoid duplicate registrations
# that bypass rate limiting.
api_router = APIRouter()
