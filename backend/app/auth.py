from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db, settings

# HTTPBearer en vez de OAuth2PasswordBearer: nuestro login no sigue el flujo
# estándar de OAuth2 (recibe JSON con rol/identificacion/contrasena, no un
# formulario username/password), así que HTTPBearer es más simple y hace que
# el botón "Authorize" de Swagger solo pida pegar el token, sin más campos.
security_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        identificacion: Optional[str] = payload.get("sub")
        rol: Optional[str] = payload.get("rol")
        if identificacion is None or rol is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return {"identificacion": identificacion, "rol": rol, "payload": payload}