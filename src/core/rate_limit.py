from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter with remote address as default key
limiter = Limiter(key_func=get_remote_address)
