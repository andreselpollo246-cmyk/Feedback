from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any

from ..database import get_db
from ..models import Aprendiz, Instructor, Administracion, Ficha, ProgramaFormacion
from ..auth import create_access_token  

#IMPORT RELATIVO 

router = APIRouter()

class LoginRequest(BaseModel):
    rol: str
    identificacion: str
    contrasena: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    rol: str
    nombre: str
    identificacion: str
    id_usuario: int | None = None
    ficha: str | None = None
    programa: str | None = None

@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)) -> dict[str, Any]: # Esto le dice a Pylance: "esta función devuelve un diccionario cuyas claves son texto (str), y cuyos valores pueden ser de cualquier tipo (Any)". Como tu return mezcla strings, enteros y None en un mismo diccionario, Any es la forma honesta de decir "no voy a restringir qué tipo de valor lleva cada clave". Any viene de from typing import Any.
    rol = datos.rol.lower().strip()
    identificacion = datos.identificacion.strip()
    contrasena = datos.contrasena

    if rol not in ["aprendiz", "instructor", "admin"]:
        raise HTTPException(status_code=400, detail="Rol no válido")

    usuario = None
    nombre: str = ""
    id_usuario: Optional[int] = None
    ficha: Optional[str] = None
    programa: Optional[str] = None

    if rol == "aprendiz":
        usuario = db.query(Aprendiz).filter(
            Aprendiz.NumDoc == identificacion,
            Aprendiz.Contrasena == contrasena
        ).first()
        if usuario:
            id_usuario = usuario.IdAprendiz
            nombre = f"{usuario.Nombres} {usuario.Apellidos}"
            ficha_obj = db.query(Ficha).filter(Ficha.IdFicha == usuario.IdFicha).first()
            if ficha_obj:
                ficha = ficha_obj.NumeroFicha
                prog = db.query(ProgramaFormacion).filter(
                    ProgramaFormacion.IdProgramaF == ficha_obj.IdProgramaF
                ).first()
                programa = prog.NombrePrograma if prog else ""

    elif rol == "instructor":
        usuario = db.query(Instructor).filter(
            Instructor.NumDoc == identificacion,
            Instructor.Contrasena == contrasena
        ).first()
        if usuario:
            id_usuario = usuario.IdInstructor
            nombre = f"{usuario.Nombres} {usuario.Apellidos}"
            programa = "Instructor SENA"

    elif rol == "admin":
        usuario = db.query(Administracion).filter(
            Administracion.NombreUsuario == identificacion,
            Administracion.Contrasena == contrasena
        ).first()
        if usuario:
            id_usuario = usuario.IdAdmin
            nombre = f"{usuario.nombres} {usuario.apellidos}"
            programa = "Administrador SENA"

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario, contraseña o rol incorrectos"
        )

    access_token = create_access_token(
        data={
            "sub": identificacion,
            "rol": rol,
            "id_usuario": id_usuario,
            "nombre": nombre
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": rol,
        "nombre": nombre,
        "identificacion": identificacion,
        "id_usuario": id_usuario,
        "ficha": ficha,
        "programa": programa
    }


# Este sí era un bug de lógica, no de tipos. Tu TokenResponse (el modelo de respuesta que Pydantic usa para validar y serializar lo que devuelves) define el campo como ficha (minúscula). Si en el return pones "Ficha" (mayúscula), Pydantic no encuentra coincidencia exacta y ese dato se pierde silenciosamente — el frontend siempre recibiría ficha: null, aunque el aprendiz sí tuviera ficha asignada en la base de datos. Por eso lo corregimos a minúscula.
