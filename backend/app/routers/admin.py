import uuid
from datetime import date
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Administracion,
    Aprendiz,
    Instructor,
    Ficha,
    ProgramaFormacion,
    nivelformacion,
    Competencia,
    competenciainstructor,
    AsignacionInstructor,
    Trimestre,
    Evaluacion,
)

router = APIRouter()


# ======================
# Config de fotos de instructor (equivalente a guardar_foto_instructor en Flask)
# ======================

CARPETA_FOTOS_INSTRUCTOR = Path(__file__).resolve().parent.parent / "static" / "img" / "instructores"
RUTA_PUBLICA_FOTOS_INSTRUCTOR = "/static/img/instructores"
FOTO_MAX_BYTES = 2 * 1024 * 1024  # 2 MB
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


def guardar_foto_instructor(archivo: Optional[UploadFile]) -> tuple[Optional[str], Optional[str]]:
    """Valida y guarda la foto PNG de un instructor.

    Devuelve (ruta_publica, None) si todo salió bien,
    o (None, mensaje_de_error) si el archivo no es válido.
    Si no se envió archivo devuelve (None, None): la foto es opcional.
    """
    if archivo is None or not archivo.filename:
        return None, None

    if not archivo.filename.lower().endswith(".png"):
        return None, "La foto debe ser un archivo PNG."

    contenido = archivo.file.read()
    archivo.file.seek(0)

    if len(contenido) == 0:
        return None, "El archivo de la foto está vacío."

    if len(contenido) > FOTO_MAX_BYTES:
        return None, "La foto supera el tamaño máximo de 2 MB."

    if contenido[: len(FIRMA_PNG)] != FIRMA_PNG:
        return None, "El archivo no es una imagen PNG válida."

    nombre_final = f"{uuid.uuid4().hex}.png"
    CARPETA_FOTOS_INSTRUCTOR.mkdir(parents=True, exist_ok=True)
    with open(CARPETA_FOTOS_INSTRUCTOR / nombre_final, "wb") as f:
        f.write(contenido)

    return f"{RUTA_PUBLICA_FOTOS_INSTRUCTOR}/{nombre_final}", None


def requerir_admin(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado. Solo administradores.")
    return current_user


# ======================
# 1. Dashboard (totales)
# ======================

class AdminDashboard(BaseModel):
    nombre: str
    identificacion: str
    total_aprendices: int
    total_instructores: int
    total_evaluaciones: int


@router.get("/dashboard", response_model=AdminDashboard)
def dashboard_admin(
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
) -> AdminDashboard:
    id_usuario = current_user["payload"].get("id_usuario")
    admin = db.query(Administracion).filter(Administracion.IdAdmin == id_usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")

    total_aprendices = db.query(func.count(Aprendiz.IdAprendiz)).scalar() or 0
    total_instructores = db.query(func.count(Instructor.IdInstructor)).scalar() or 0
    total_evaluaciones = db.query(func.count(Evaluacion.idevaluacion)).scalar() or 0

    return AdminDashboard(
        nombre=f"{admin.nombres} {admin.apellidos}",
        identificacion=admin.NombreUsuario,
        total_aprendices=total_aprendices,
        total_instructores=total_instructores,
        total_evaluaciones=total_evaluaciones,
    )


# ======================
# 2. Crear aprendiz
# ======================

class CrearAprendizRequest(BaseModel):
    nombre: str
    apellido: str
    fechaNacimiento: date
    correo: str
    password: str
    tipoDocumento: str
    numeroDocumento: str
    ficha: str


@router.post("/crear-aprendiz")
def crear_aprendiz(
    datos: CrearAprendizRequest,
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    num_doc = datos.numeroDocumento.strip()

    existe = db.query(Aprendiz).filter(Aprendiz.NumDoc == num_doc).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese número de documento.")

    ficha_valor = datos.ficha.strip()
    ficha_obj = db.query(Ficha).filter(Ficha.NumeroFicha == ficha_valor).first()
    if not ficha_obj:
        raise HTTPException(status_code=400, detail=f"No existe una ficha con el número {ficha_valor}.")

    id_admin = current_user["payload"].get("id_usuario")

    nuevo = Aprendiz(
        Nombres=datos.nombre,
        Apellidos=datos.apellido,
        FechaNacimiento=datos.fechaNacimiento,
        Correo=datos.correo,
        Contrasena=datos.password,
        TipoDoc=datos.tipoDocumento,
        NumDoc=num_doc,
        IdAdmin=id_admin,
        IdFicha=ficha_obj.IdFicha,
    )
    db.add(nuevo)
    db.commit()

    return {
        "success": True,
        "message": "Aprendiz creado correctamente.",
        "usuario": {"identificacion": num_doc, "nombre": f"{datos.nombre} {datos.apellido}"},
    }


# ======================
# 3. Crear instructor (multipart/form-data: incluye foto opcional)
# ======================

@router.post("/crear-instructor")
def crear_instructor(
    nombre: str = Form(...),
    apellido: str = Form(...),
    fechaNacimiento: date = Form(...),
    correo: str = Form(...),
    password: str = Form(...),
    tipoDocumento: str = Form(...),
    numeroDocumento: str = Form(...),
    competencia: str = Form(""),
    ficha: str = Form(""),
    foto: Optional[UploadFile] = File(None),
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    num_doc = numeroDocumento.strip()

    existe = db.query(Instructor).filter(Instructor.NumDoc == num_doc).first()
    if existe:
        raise HTTPException(status_code=409, detail="Ya existe un instructor con ese número de documento.")

    # Validar y guardar la foto ANTES de insertar en la base de datos
    foto_url, error_foto = guardar_foto_instructor(foto)
    if error_foto:
        raise HTTPException(status_code=400, detail=error_foto)

    id_admin = current_user["payload"].get("id_usuario")

    nuevo_instructor = Instructor(
        Nombres=nombre,
        Apellidos=apellido,
        FechaNacimiento=fechaNacimiento,
        Correo=correo,
        Contrasena=password,
        Foto_URL=foto_url,
        TipoDoc=tipoDocumento,
        NumDoc=num_doc,
        IdAdmin=id_admin,
    )
    db.add(nuevo_instructor)
    db.commit()
    db.refresh(nuevo_instructor)

    # Si viene competencia, crear/actualizar la asignación (igual que en Flask)
    competencia_texto = competencia.strip()
    if competencia_texto:
        comp = db.query(Competencia).filter(Competencia.Nombre_Competencia == competencia_texto).first()
        if not comp:
            comp = Competencia(Nombre_Competencia=competencia_texto, IdAdmin=id_admin)
            db.add(comp)
            db.commit()
            db.refresh(comp)

        trimestre = (
            db.query(Trimestre)
            .filter(
                Trimestre.FechaInicio <= date.today(),
                Trimestre.FechaFin >= date.today(),
                Trimestre.Estado == True,  # noqa: E712
            )
            .first()
        )

        ficha_valor = ficha.strip()
        id_ficha = None
        if ficha_valor:
            ficha_obj = db.query(Ficha).filter(Ficha.NumeroFicha == ficha_valor).first()
            if not ficha_obj:
                raise HTTPException(status_code=400, detail=f"No existe una ficha con el número {ficha_valor}.")
            id_ficha = ficha_obj.IdFicha

        if comp and trimestre:
            db.add(
                AsignacionInstructor(
                    IdInstructor=nuevo_instructor.IdInstructor,
                    IdCompetencia=comp.IdCompetencia,
                    IdTrimestre=trimestre.IdTrimestre,
                    IdFicha=id_ficha,
                    Habilitado=True,
                )
            )
            db.commit()

    return {
        "success": True,
        "message": "Instructor creado correctamente.",
        "usuario": {
            "identificacion": num_doc,
            "nombre": f"{nombre} {apellido}",
            "foto_url": foto_url,
        },
    }


# ======================
# 4. Listar instructores
# ======================

class InstructorListItem(BaseModel):
    id: int
    nombre: str
    numDoc: str
    correo: Optional[str] = None
    fotoUrl: Optional[str] = None


@router.get("/instructores", response_model=List[InstructorListItem])
def listar_instructores(
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
) -> List[InstructorListItem]:
    instructores = db.query(Instructor).order_by(Instructor.Nombres).all()
    return [
        InstructorListItem(
            id=i.IdInstructor,
            nombre=f"{i.Nombres} {i.Apellidos}",
            numDoc=i.NumDoc,
            correo=i.Correo,
            fotoUrl=i.Foto_URL,
        )
        for i in instructores
    ]


# ======================
# 5. Listar fichas
# ======================

class FichaListItem(BaseModel):
    id: int
    numero: str
    inicio: Optional[str] = None
    fin: Optional[str] = None
    modalidad: Optional[str] = None
    programa: Optional[str] = None
    nivel: Optional[str] = None


@router.get("/fichas", response_model=List[FichaListItem])
def listar_fichas(
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
) -> List[FichaListItem]:
    filas = (
        db.query(Ficha, ProgramaFormacion, nivelformacion)
        .join(ProgramaFormacion, Ficha.IdProgramaF == ProgramaFormacion.IdProgramaF)
        .join(nivelformacion, Ficha.IdNivel == nivelformacion.IdNivel)
        .order_by(Ficha.NumeroFicha)
        .all()
    )
    return [
        FichaListItem(
            id=ficha.IdFicha,
            numero=ficha.NumeroFicha,
            inicio=str(ficha.InicioFormacion) if ficha.InicioFormacion else None,
            fin=str(ficha.FinFormacion) if ficha.FinFormacion else None,
            modalidad=ficha.modalidad,
            programa=programa.NombrePrograma,
            nivel=nivel.nivelformacion,
        )
        for ficha, programa, nivel in filas
    ]


# ======================
# 6. Listar competencias
# ======================

class CompetenciaListItem(BaseModel):
    id: int
    nombre: str


@router.get("/competencias", response_model=List[CompetenciaListItem])
def listar_competencias(
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
) -> List[CompetenciaListItem]:
    comps = db.query(Competencia).order_by(Competencia.Nombre_Competencia).all()
    return [CompetenciaListItem(id=c.IdCompetencia, nombre=c.Nombre_Competencia) for c in comps]


# ======================
# 7. Asignar instructor a ficha/competencia/trimestre
# ======================

class AsignarInstructorRequest(BaseModel):
    idInstructor: int
    numeroFicha: str
    idCompetencia: int
    idTrimestre: int
    habilitado: bool = True


@router.post("/asignar-instructor")
def asignar_instructor(
    datos: AsignarInstructorRequest,
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    instructor = db.query(Instructor).filter(Instructor.IdInstructor == datos.idInstructor).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado.")

    ficha_obj = db.query(Ficha).filter(Ficha.NumeroFicha == datos.numeroFicha).first()
    if not ficha_obj:
        raise HTTPException(status_code=404, detail=f"No existe una ficha con el número {datos.numeroFicha}.")

    comp = db.query(Competencia).filter(Competencia.IdCompetencia == datos.idCompetencia).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competencia no encontrada.")

    trimestre = db.query(Trimestre).filter(Trimestre.IdTrimestre == datos.idTrimestre).first()
    if not trimestre:
        raise HTTPException(status_code=404, detail="Trimestre no encontrado.")

    # Si el instructor no tenía relación con esta competencia, se crea automáticamente
    rel = (
        db.query(competenciainstructor)
        .filter(
            competenciainstructor.IdCompetencia == datos.idCompetencia,
            competenciainstructor.IdInstructor == datos.idInstructor,
        )
        .first()
    )
    if not rel:
        db.add(competenciainstructor(IdCompetencia=datos.idCompetencia, IdInstructor=datos.idInstructor))

    existente = (
        db.query(AsignacionInstructor)
        .filter(
            AsignacionInstructor.IdInstructor == datos.idInstructor,
            AsignacionInstructor.IdFicha == ficha_obj.IdFicha,
            AsignacionInstructor.IdCompetencia == datos.idCompetencia,
            AsignacionInstructor.IdTrimestre == datos.idTrimestre,
        )
        .first()
    )

    if existente:
        existente.Habilitado = datos.habilitado
        accion = "actualizada"
        status_code = 200
    else:
        db.add(
            AsignacionInstructor(
                IdInstructor=datos.idInstructor,
                IdFicha=ficha_obj.IdFicha,
                IdCompetencia=datos.idCompetencia,
                IdTrimestre=datos.idTrimestre,
                Habilitado=datos.habilitado,
            )
        )
        accion = "creada"
        status_code = 201

    db.commit()

    return JSONResponse(
        status_code=status_code,
        content={"success": True, "message": f"Asignación {accion} correctamente."},
    )


# ======================
# 8. Listar asignaciones actuales
# ======================

class AsignacionListItem(BaseModel):
    id: int
    instructor: str
    numDoc: str
    ficha: str
    programa: str
    competencia: str
    trimestre: str
    trimestreActivo: bool
    habilitado: bool


@router.get("/asignaciones", response_model=List[AsignacionListItem])
def listar_asignaciones(
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
) -> List[AsignacionListItem]:
    filas = (
        db.query(AsignacionInstructor, Instructor, Ficha, ProgramaFormacion, Competencia, Trimestre)
        .join(Instructor, AsignacionInstructor.IdInstructor == Instructor.IdInstructor)
        .join(Ficha, AsignacionInstructor.IdFicha == Ficha.IdFicha)
        .join(ProgramaFormacion, Ficha.IdProgramaF == ProgramaFormacion.IdProgramaF)
        .join(Competencia, AsignacionInstructor.IdCompetencia == Competencia.IdCompetencia)
        .join(Trimestre, AsignacionInstructor.IdTrimestre == Trimestre.IdTrimestre)
        .order_by(Trimestre.FechaInicio.desc(), Instructor.Nombres)
        .all()
    )
    return [
        AsignacionListItem(
            id=asignacion.IdAsignacion,
            instructor=f"{instructor.Nombres} {instructor.Apellidos}",
            numDoc=instructor.NumDoc,
            ficha=ficha.NumeroFicha,
            programa=programa.NombrePrograma,
            competencia=competencia.Nombre_Competencia,
            trimestre=trimestre.NombreTrimestre,
            trimestreActivo=trimestre.Estado,
            habilitado=asignacion.Habilitado,
        )
        for asignacion, instructor, ficha, programa, competencia, trimestre in filas
    ]


# ======================
# 9. Eliminar asignación
# ======================

@router.delete("/eliminar-asignacion/{id_asignacion}")
def eliminar_asignacion(
    id_asignacion: int,
    current_user: dict[str, Any] = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    asignacion = db.query(AsignacionInstructor).filter(AsignacionInstructor.IdAsignacion == id_asignacion).first()
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")

    db.delete(asignacion)
    db.commit()

    return {"success": True, "message": "Asignación eliminada correctamente."}