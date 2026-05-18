"""
app/routes/auth.py
Autenticação JWT mínima — M4-04.
POST /auth/login → retorna token JWT
"""

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import get_db
from models.repositorios_CRUD import UsuarioRepo

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------------------------------------------------------------------------
# Configuração JWT
# ---------------------------------------------------------------------------

SECRET_KEY  = os.getenv("SECRET_KEY", "easyfriend-secret-dev-key-trocar-em-prod")
ALGORITHM   = "HS256"
EXPIRE_MIN  = 60 * 24  # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    try:
        return pwd_context.verify(senha_plain, senha_hash)
    except Exception:
        # Fallback: comparação direta para seeds de dev que não usam bcrypt
        return senha_plain == senha_hash


def _criar_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Autentica o usuário e retorna um token JWT.
    O iOS armazena esse token no Keychain e envia em cada requisição.

    Body (form-data):
        username: email do usuário
        password: senha
    """
    usuario = UsuarioRepo.buscar_por_email(db, form.username)

    if not usuario or not _verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = _criar_token({"sub": str(usuario.id), "email": usuario.email})

    return {
        "access_token": token,
        "token_type":   "bearer",
        "usuario_id":   usuario.id,
        "nome":         usuario.nome,
    }


@router.get("/me")
def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retorna os dados do usuário autenticado (valida o token)."""
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id  = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )

    usuario = UsuarioRepo.buscar_por_id(db, user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return {
        "usuario_id":  usuario.id,
        "nome":        usuario.nome,
        "email":       usuario.email,
        "idioma":      usuario.idioma,
        "pais_origem": usuario.pais_origem,
    }
