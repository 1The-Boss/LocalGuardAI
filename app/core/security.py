import bcrypt
from passlib.context import CryptContext

# Fix passlib 1.7.4 compatibility issue with bcrypt >= 4.0.0
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")})

_orig_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(salt, str):
        salt = salt.encode("utf-8")
    if len(password) > 72:
        password = password[:72]
    return _orig_hashpw(password, salt)
bcrypt.hashpw = _patched_hashpw

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
