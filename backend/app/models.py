from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ProgramaFormacion(Base):
    __tablename__ = "programaformacion"

    IdProgramaF: Mapped[int] = mapped_column(primary_key=True, index=True)
    NombrePrograma: Mapped[str] = mapped_column(String(150))
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

    fichas: Mapped[List["Ficha"]] = relationship(back_populates="programa")


class Ficha(Base):
    __tablename__ = "ficha"

    IdFicha: Mapped[int] = mapped_column(primary_key=True, index=True)
    NumeroFicha: Mapped[str] = mapped_column(String(20), unique=True)
    InicioFormacion: Mapped[Optional[date]] = mapped_column(Date)
    FinFormacion: Mapped[Optional[date]] = mapped_column(Date)
    modalidad: Mapped[Optional[str]] = mapped_column(String(50))
    IdNivel: Mapped[Optional[int]]
    IdProgramaF: Mapped[Optional[int]] = mapped_column(ForeignKey("programaformacion.IdProgramaF"))
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

    programa: Mapped[Optional["ProgramaFormacion"]] = relationship(back_populates="fichas")
    aprendices: Mapped[List["Aprendiz"]] = relationship(back_populates="ficha")
    asignaciones: Mapped[List["AsignacionInstructor"]] = relationship(back_populates="ficha")


class Aprendiz(Base):
    __tablename__ = "aprendiz"

    IdAprendiz: Mapped[int] = mapped_column(primary_key=True, index=True)
    Nombres: Mapped[str] = mapped_column(String(100))
    Apellidos: Mapped[str] = mapped_column(String(100))
    FechaNacimiento: Mapped[Optional[date]] = mapped_column(Date)
    Correo: Mapped[Optional[str]] = mapped_column(String(150))
    Contrasena: Mapped[str] = mapped_column(String(255))
    TipoDoc: Mapped[Optional[str]] = mapped_column(String(20))
    NumDoc: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))
    IdFicha: Mapped[Optional[int]] = mapped_column(ForeignKey("ficha.IdFicha"))

    ficha: Mapped[Optional["Ficha"]] = relationship(back_populates="aprendices")
    evaluaciones: Mapped[List["Evaluacion"]] = relationship(back_populates="aprendiz")


class Instructor(Base):
    __tablename__ = "instructor"

    IdInstructor: Mapped[int] = mapped_column(primary_key=True, index=True)
    Nombres: Mapped[str] = mapped_column(String(100))
    Apellidos: Mapped[str] = mapped_column(String(100))
    FechaNacimiento: Mapped[Optional[date]] = mapped_column(Date)
    Correo: Mapped[Optional[str]] = mapped_column(String(150), unique=True)
    Contrasena: Mapped[str] = mapped_column(String(255))
    Foto_URL: Mapped[Optional[str]] = mapped_column(String(255))
    TipoDoc: Mapped[Optional[str]] = mapped_column(String(20))
    NumDoc: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

    asignaciones: Mapped[List["AsignacionInstructor"]] = relationship(back_populates="instructor")
    evaluaciones: Mapped[List["Evaluacion"]] = relationship(back_populates="instructor")


class NivelFormacion(Base):
    __tablename__ = "nivelformacion"

    IdNivel: Mapped[int] = mapped_column(primary_key=True, index=True)
    nivelformacion: Mapped[str] = mapped_column(String(50))


class Administracion(Base):
    __tablename__ = "administracion"

    IdAdmin: Mapped[int] = mapped_column(primary_key=True, index=True)
    NombreUsuario: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    numdoc: Mapped[Optional[str]] = mapped_column(String(20))
    correo: Mapped[Optional[str]] = mapped_column(String(150), unique=True)
    Contrasena: Mapped[str] = mapped_column(String(255))


class Trimestre(Base):
    __tablename__ = "trimestre"

    IdTrimestre: Mapped[int] = mapped_column(primary_key=True, index=True)
    NombreTrimestre: Mapped[str] = mapped_column(String(50))
    FechaInicio: Mapped[Optional[date]] = mapped_column(Date)
    FechaFin: Mapped[Optional[date]] = mapped_column(Date)
    Estado: Mapped[bool] = mapped_column(Boolean, default=True)

    asignaciones: Mapped[List["AsignacionInstructor"]] = relationship(back_populates="trimestre")
    evaluaciones: Mapped[List["Evaluacion"]] = relationship(back_populates="trimestre")


class Competencia(Base):
    __tablename__ = "competencia"

    IdCompetencia: Mapped[int] = mapped_column(primary_key=True, index=True)
    Nombre_Competencia: Mapped[str] = mapped_column(String(150))
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

    asignaciones: Mapped[List["AsignacionInstructor"]] = relationship(back_populates="competencia")


class CompetenciaInstructor(Base):
    __tablename__ = "competencia_instructor"

    IdCompetencia: Mapped[int] = mapped_column(ForeignKey("competencia.IdCompetencia"), primary_key=True)
    IdInstructor: Mapped[int] = mapped_column(ForeignKey("instructor.IdInstructor"), primary_key=True)


class Criterio(Base):
    __tablename__ = "criterio"

    IdCriterio: Mapped[int] = mapped_column(primary_key=True, index=True)
    TextoCriterio: Mapped[str] = mapped_column(String(255))


class AsignacionInstructor(Base):
    __tablename__ = "asignacion_instructor"

    IdAsignacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    IdInstructor: Mapped[int] = mapped_column(ForeignKey("instructor.IdInstructor"))
    IdFicha: Mapped[int] = mapped_column(ForeignKey("ficha.IdFicha"))
    IdCompetencia: Mapped[int] = mapped_column(ForeignKey("competencia.IdCompetencia"))
    IdTrimestre: Mapped[int] = mapped_column(ForeignKey("trimestre.IdTrimestre"))
    Habilitado: Mapped[bool] = mapped_column(Boolean, default=True)

    instructor: Mapped["Instructor"] = relationship(back_populates="asignaciones")
    ficha: Mapped["Ficha"] = relationship(back_populates="asignaciones")
    competencia: Mapped["Competencia"] = relationship(back_populates="asignaciones")
    trimestre: Mapped["Trimestre"] = relationship(back_populates="asignaciones")


class Evaluacion(Base):
    __tablename__ = "evaluacion"

    idevaluacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    fecha: Mapped[Optional[datetime]] = mapped_column(DateTime)
    inicio: Mapped[Optional[date]] = mapped_column(Date)
    fin: Mapped[Optional[date]] = mapped_column(Date)
    comentario: Mapped[Optional[str]] = mapped_column(String(500))
    evaluado: Mapped[bool] = mapped_column(Boolean, default=False)
    IdAprendiz: Mapped[Optional[int]] = mapped_column(ForeignKey("aprendiz.IdAprendiz"))
    IdInstructor: Mapped[Optional[int]] = mapped_column(ForeignKey("instructor.IdInstructor"))
    IdTrimestre: Mapped[Optional[int]] = mapped_column(ForeignKey("trimestre.IdTrimestre"))

    aprendiz: Mapped[Optional["Aprendiz"]] = relationship(back_populates="evaluaciones")
    instructor: Mapped[Optional["Instructor"]] = relationship(back_populates="evaluaciones")
    trimestre: Mapped[Optional["Trimestre"]] = relationship(back_populates="evaluaciones")
    detalles: Mapped[List["DetalleEvaluacion"]] = relationship(back_populates="evaluacion")


class DetalleEvaluacion(Base):
    __tablename__ = "detalle_evaluacion"

    IdDetalle: Mapped[int] = mapped_column(primary_key=True, index=True)
    IdEvaluacion: Mapped[Optional[int]] = mapped_column(ForeignKey("evaluacion.idevaluacion"))
    IdCriterio: Mapped[Optional[int]] = mapped_column(ForeignKey("criterio.IdCriterio"))
    Calificacion: Mapped[Optional[int]]

    evaluacion: Mapped[Optional["Evaluacion"]] = relationship(back_populates="detalles")
    criterio: Mapped[Optional["Criterio"]] = relationship()
#Si models.py no tiene nada escrito, entonces Aprendiz, Instructor, etc. simplemente no existen como objetos Python

# Optional[int] es literalmente un atajo de int | None. Le dice a Pylance: "esta variable puede contener un número entero, o puede estar vacía (None)". Es exactamente tu situación: al inicio de login() no sabes si el usuario existe, así que id_usuario arranca en None, y solo si se encuentra el usuario en la base de datos se llena con un número real.

