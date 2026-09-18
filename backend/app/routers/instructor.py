from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    Instructor,
    Ficha,
    ProgramaFormacion,
    Competencia,
    AsignacionInstructor,
    Trimestre,
    Aprendiz,
    Evaluacion,
    detalleEvaluacion,
)

router = APIRouter()


# ======================
# Schemas de respuesta
# ======================

class ComentarioItem(BaseModel):
    estrellas: int
    texto: str
    tipo: str


class FichaStats(BaseModel):
    programa: Optional[str] = None
    competencia: str
    promedio: float
    total: int
    porcentaje: int
    rendimiento: str
    mensaje: str
    comentarios: List[ComentarioItem]


class InstructorDashboard(BaseModel):
    nombre: str
    identificacion: str
    fichas_data: Dict[str, FichaStats]


# ======================
# Endpoint principal
# ======================

@router.get("/dashboard", response_model=InstructorDashboard)
def dashboard_instructor(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InstructorDashboard:
    # 1. Verificar que sea instructor
    if current_user["rol"] != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado. Solo instructores.",
        )

    id_usuario = current_user["payload"].get("id_usuario")

    # 2. Obtener datos del instructor
    instructor = db.query(Instructor).filter(Instructor.IdInstructor == id_usuario).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")

    nombre = f"{instructor.Nombres} {instructor.Apellidos}"
    identificacion = instructor.NumDoc

    # 3. Fichas/competencias asignadas a este instructor (Habilitado = True)
    asignaciones = (
        db.query(AsignacionInstructor, Ficha, ProgramaFormacion, Competencia, Trimestre)
        .join(Ficha, AsignacionInstructor.IdFicha == Ficha.IdFicha)
        .join(ProgramaFormacion, Ficha.IdProgramaF == ProgramaFormacion.IdProgramaF)
        .join(Competencia, AsignacionInstructor.IdCompetencia == Competencia.IdCompetencia)
        .join(Trimestre, AsignacionInstructor.IdTrimestre == Trimestre.IdTrimestre)
        .filter(
            AsignacionInstructor.IdInstructor == instructor.IdInstructor,
            AsignacionInstructor.Habilitado == True,  # noqa: E712
        )
        .all()
    )

    fichas_data: Dict[str, FichaStats] = {}

    for _asignacion, ficha, programa, competencia, trimestre in asignaciones:
        # 4. Estadísticas: promedio de calificación y total de evaluaciones
        aprendices_ficha = db.query(Aprendiz.IdAprendiz).filter(Aprendiz.IdFicha == ficha.IdFicha)

        stats = (
            db.query(
                func.avg(detalleEvaluacion.Calificacion).label("promedio"),
                func.count(func.distinct(Evaluacion.idevaluacion)).label("total"),
            )
            .join(detalleEvaluacion, Evaluacion.idevaluacion == detalleEvaluacion.IdEvaluacion)
            .filter(
                Evaluacion.IdInstructor == instructor.IdInstructor,
                Evaluacion.IdTrimestre == trimestre.IdTrimestre,
                Evaluacion.IdAprendiz.in_(aprendices_ficha),
            )
            .first()
        )

        promedio = float(stats.promedio) if stats and stats.promedio else 0.0
        total = int(stats.total) if stats and stats.total else 0

        # 5. Comentarios recientes (últimos 5, no vacíos)
        comentarios_db = (
            db.query(Evaluacion.comentario)
            .filter(
                Evaluacion.IdInstructor == instructor.IdInstructor,
                Evaluacion.IdTrimestre == trimestre.IdTrimestre,
                Evaluacion.comentario.isnot(None),
                Evaluacion.comentario != "",
            )
            .order_by(Evaluacion.fecha.desc())
            .limit(5)
            .all()
        )

        comentarios = [
            ComentarioItem(estrellas=5, texto=texto, tipo="positivo")
            for (texto,) in comentarios_db
        ]

        # Igual que en Flask: la clave es el número de ficha. Si el instructor
        # tiene varias competencias asignadas a la MISMA ficha, solo queda
        # registrada la última que se procese (comportamiento heredado del original).
        fichas_data[ficha.NumeroFicha] = FichaStats(
            programa=programa.NombrePrograma,
            competencia=competencia.Nombre_Competencia,
            promedio=round(promedio, 1),
            total=total,
            porcentaje=min(int((promedio / 5) * 100), 100),
            rendimiento="Excelente" if promedio >= 4 else "Bueno" if promedio >= 3 else "Regular",
            mensaje=(
                "¡Vas por buen camino! Sigue así."
                if promedio >= 4
                else "Hay espacio para mejorar en la claridad de las explicaciones."
            ),
            comentarios=comentarios,
        )

    return InstructorDashboard(
        nombre=nombre,
        identificacion=identificacion,
        fichas_data=fichas_data,
    )