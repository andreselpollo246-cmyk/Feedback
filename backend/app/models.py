from datetime import date
from typing import Optional, List

from sqlalchemy import String, Date, ForeignKey
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


class Aprendiz(Base):
    __tablename__ = "aprendiz"

    IdAprendiz: Mapped[int] = mapped_column(primary_key=True, index=True)   #Aquí le dices explícitamente a Python y a Pylance: "cuando accedas a una instancia (usuario.IdAprendiz), vas a recibir un int de verdad". Mapped[int] es la anotación de tipo; mapped_column(...) es la configuración real de la columna en la base de datos (tipo SQL, si es primary key, etc.). Con este cambio, usuario.IdAprendiz ya se ve como int normal, y por eso desaparecieron los errores de "no se puede asignar Column[int] a int | None".
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
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))
    Estado: Mapped[Optional[str]] = mapped_column(String(20))

class AsignacionInstructor(Base):
    __tablename__ = "asignacioninstructor"

    IdAsignacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    IdInstructor: Mapped[Optional[int]] = mapped_column(ForeignKey("instructor.IdInstructor"))
    IdFicha: Mapped[Optional[int]] = mapped_column(ForeignKey("ficha.IdFicha"))
    IdCompetencia: Mapped[Optional[int]] = mapped_column(ForeignKey("competencia.IdCompetencia"))
    IdTrimestre: Mapped[Optional[int]] = mapped_column(ForeignKey("trimestre.IdTrimestre"))
    Habilitado: Mapped[Optional[bool]] = mapped_column(default=True)

class Competencia(Base):
    __tablename__ = "competencia"

    IdCompetencia: Mapped[int] = mapped_column(primary_key=True, index=True)
    Nombre_Competencia: Mapped[str] = mapped_column(String(100))
    Descripcion: Mapped[Optional[str]] = mapped_column(String(255))
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

class Evaluacion(Base):
    __tablename__ = "evaluacion"

    IdEvaluacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    IdAprendiz: Mapped[Optional[int]] = mapped_column(ForeignKey("aprendiz.IdAprendiz"))
    IdInstructor: Mapped[Optional[int]] = mapped_column(ForeignKey("instructor.IdInstructor"))
    IdTrimestre: Mapped[Optional[int]] = mapped_column(ForeignKey("trimestre.IdTrimestre"))
    FechaEvaluacion: Mapped[Optional[date]] = mapped_column(Date)
    Comentarios: Mapped[Optional[str]] = mapped_column(String(255))

class detalleEvaluacion(Base):
    __tablename__ = "detalleevaluacion"

    IdDetalleEvaluacion: Mapped[int] = mapped_column(primary_key=True, index=True)
    IdEvaluacion: Mapped[Optional[int]] = mapped_column(ForeignKey("evaluacion.IdEvaluacion"))
    IdCriterio: Mapped[Optional[int]] = mapped_column(ForeignKey("criterio.IdCriterio"))
    Calificacion: Mapped[Optional[int]] = mapped_column()

class nivelformacion(Base):
    __tablename__ = "nivelformacion"

    IdNivel: Mapped[int] = mapped_column(primary_key=True, index=True)
    NombreNivel: Mapped[str] = mapped_column(String(50))
    Descripcion: Mapped[Optional[str]] = mapped_column(String(255))
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

class competenciainstructor(Base):
    __tablename__ = "competenciainstructor"

    IdCompetenciaInstructor: Mapped[int] = mapped_column(primary_key=True, index=True)
    IdInstructor: Mapped[Optional[int]] = mapped_column(ForeignKey("instructor.IdInstructor"))
    IdCompetencia: Mapped[Optional[int]] = mapped_column(ForeignKey("competencia.IdCompetencia"))
    IdAdmin: Mapped[Optional[int]] = mapped_column(ForeignKey("administracion.IdAdmin"))

#Si models.py no tiene nada escrito, entonces Aprendiz, Instructor, etc. simplemente no existen como objetos Python

# Optional[int] es literalmente un atajo de int | None. Le dice a Pylance: "esta variable puede contener un número entero, o puede estar vacía (None)". Es exactamente tu situación: al inicio de login() no sabes si el usuario existe, así que id_usuario arranca en None, y solo si se encuentra el usuario en la base de datos se llena con un número real.

