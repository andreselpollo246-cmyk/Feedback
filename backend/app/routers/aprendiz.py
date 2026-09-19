from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
#from sqlalchemy import text
from datetime import date, datetime, timezone
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Aprendiz, Instructor, Ficha, ProgramaFormacion,
    AsignacionInstructor, Competencia, Trimestre, Evaluacion, DetalleEvaluacion
)

router = APIRouter()

# Mapeo fijo de nombre de criterio (tal como lo manda el frontend) -> IdCriterio real
# en la base de datos. Igual al de la versión Flask original.
MAPA_CRITERIOS = {
    "dominio": 1,
    "claridad": 2,
    "puntualidad": 3,
    "trato": 4,
    "metodologia": 5,
}

# ======================
# Schemas de respuesta
# ======================

class InstructorAprendiz(BaseModel):
    id: int
    nombre: str
    ficha: str
    competencia: str
    imagen: Optional[str] = None
    evaluado: bool

class AprendizDashboard(BaseModel):
    nombre: str
    identificacion: str
    ficha: Optional[str] = None
    programa: Optional[str] = None
    trimestre: str
    instructores: List[InstructorAprendiz]

# ======================
# Endpoint principal
# ======================

@router.get("/dashboard", response_model=AprendizDashboard)
def dashboard_aprendiz(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Verificar que sea aprendiz
    if current_user["rol"] != "aprendiz":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Solo aprendices."
        )

    identificacion = current_user["identificacion"]
    id_usuario = current_user["payload"].get("id_usuario")

    # 2. Obtener datos del aprendiz
    aprendiz = db.query(Aprendiz).filter(Aprendiz.IdAprendiz == id_usuario).first()
    if not aprendiz:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")

    nombre = f"{aprendiz.Nombres} {aprendiz.Apellidos}"

    # 3. Obtener ficha y programa
    ficha_numero = None
    programa_nombre = None

    ficha_obj = db.query(Ficha).filter(Ficha.IdFicha == aprendiz.IdFicha).first()
    if ficha_obj:
        ficha_numero = ficha_obj.NumeroFicha
        prog = db.query(ProgramaFormacion).filter(
            ProgramaFormacion.IdProgramaF == ficha_obj.IdProgramaF
        ).first()
        if prog:
            programa_nombre = prog.NombrePrograma

    # 4. Obtener trimestre activo
    hoy = date.today()
    trimestre = db.query(Trimestre).filter(
        Trimestre.FechaInicio <= hoy,
        Trimestre.FechaFin >= hoy,
        Trimestre.Estado == True
    ).first()

    id_trimestre = trimestre.IdTrimestre if trimestre else None
    nombre_trimestre = trimestre.NombreTrimestre if trimestre else "N/A"

    instructores_lista = []

    if id_trimestre and ficha_obj:
        # 5. Obtener instructores asignados a la ficha + trimestre
        asignaciones = db.query(
            AsignacionInstructor,
            Instructor,
            Competencia,
            Ficha
        ).join(
            Instructor, AsignacionInstructor.IdInstructor == Instructor.IdInstructor
        ).join(
            Competencia, AsignacionInstructor.IdCompetencia == Competencia.IdCompetencia
        ).join(
            Ficha, AsignacionInstructor.IdFicha == Ficha.IdFicha
        ).filter(
            AsignacionInstructor.IdFicha == ficha_obj.IdFicha,
            AsignacionInstructor.IdTrimestre == id_trimestre,
            AsignacionInstructor.Habilitado == True
        ).all()

        for asignacion, instructor, competencia, ficha in asignaciones:
            # 6. Verificar si ya fue evaluado por este aprendiz
            evaluacion = db.query(Evaluacion).filter(
                Evaluacion.IdAprendiz == aprendiz.IdAprendiz,
                Evaluacion.IdInstructor == instructor.IdInstructor,
                Evaluacion.IdTrimestre == id_trimestre
            ).first()

            instructores_lista.append(
                InstructorAprendiz(
                    id=instructor.IdInstructor,
                    nombre=f"{instructor.Nombres} {instructor.Apellidos}",
                    ficha=ficha.NumeroFicha,
                    competencia=competencia.Nombre_Competencia,
                    imagen=instructor.Foto_URL,
                    evaluado=evaluacion is not None
                )
            )

    return AprendizDashboard(
        nombre=nombre,
        identificacion=identificacion,
        ficha=ficha_numero,
        programa=programa_nombre,
        trimestre=nombre_trimestre,
        instructores=instructores_lista
    )

# ======================
# Enviar evaluación
# ======================

class EvaluarInstructorRequest(BaseModel):
    instructor_id: int
    ratings: Dict[str, int]
    comentario: str = ""


class EvaluarInstructorResponse(BaseModel):
    success: bool
    message: str


@router.post("/evaluar", response_model=EvaluarInstructorResponse)
def evaluar_instructor(
    datos: EvaluarInstructorRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluarInstructorResponse:
    if current_user["rol"] != "aprendiz":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado. Solo aprendices.")

    id_usuario = current_user["payload"].get("id_usuario")
    aprendiz = db.query(Aprendiz).filter(Aprendiz.IdAprendiz == id_usuario).first()
    if not aprendiz:
        raise HTTPException(status_code=404, detail="Aprendiz no encontrado")

    if not datos.ratings:
        raise HTTPException(status_code=400, detail="Califica al menos un criterio.")

    hoy = date.today()
    trimestre = (
        db.query(Trimestre)
        .filter(
            Trimestre.FechaInicio <= hoy,
            Trimestre.FechaFin >= hoy,
            Trimestre.Estado == True,  # noqa: E712
        )
        .first()
    )
    if not trimestre:
        raise HTTPException(status_code=400, detail="No hay un trimestre activo.")

    evaluacion = (
        db.query(Evaluacion)
        .filter(
            Evaluacion.IdAprendiz == aprendiz.IdAprendiz,
            Evaluacion.IdInstructor == datos.instructor_id,
            Evaluacion.IdTrimestre == trimestre.IdTrimestre,
        )
        .first()
    )

    if evaluacion:
        # Ya existía: se actualiza y se reemplazan sus detalles.
        evaluacion.comentario = datos.comentario
        evaluacion.fecha = datetime.now(timezone.utc)
        db.query(DetalleEvaluacion).filter(
            DetalleEvaluacion.IdEvaluacion == evaluacion.idevaluacion
        ).delete()
    else:
        evaluacion = Evaluacion(
            inicio=hoy,
            fin=hoy,
            fecha=datetime.now(timezone.utc),
            comentario=datos.comentario,
            evaluado=True,
            IdAprendiz=aprendiz.IdAprendiz,
            IdInstructor=datos.instructor_id,
            IdTrimestre=trimestre.IdTrimestre,
        )
        db.add(evaluacion)
        db.flush()  # asigna el id generado antes de usarlo en los detalles

    for criterio_nombre, calificacion in datos.ratings.items():
        id_criterio = MAPA_CRITERIOS.get(criterio_nombre)
        if id_criterio:
            db.add(
                DetalleEvaluacion(
                    IdEvaluacion=evaluacion.idevaluacion,
                    IdCriterio=id_criterio,
                    Calificacion=int(calificacion),
                )
            )

    db.commit()

    return EvaluarInstructorResponse(success=True, message="Evaluación guardada correctamente.")