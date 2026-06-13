from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter with remote address as default key.
# default_limits act as a safety net for endpoints that have no
# explicit @limiter.limit(...) (e.g. admin/knowledge-base CRUD,
# experiments CRUD, /tasks) so they are never fully unbounded.
# Endpoints with stricter explicit limits (auth, image upload/analysis)
# are unaffected since slowapi enforces both.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
