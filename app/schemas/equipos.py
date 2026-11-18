from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from app.schemas.asignacion import AsignacionCreate, AsignacionRead


class AsignacionReadWithAttributes(AsignacionRead):
    model_config = ConfigDict(from_attributes=True)

    # Human-readable labels resolved inside the caller's tenant (UI never shows raw IDs).
    docente_nombre: str | None = None
    rol_nombre: str | None = None
    contexto_nombre: str | None = None


class AsignacionMasivaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asignaciones: list[AsignacionCreate]


class AsignacionMasivaResponse(BaseModel):
    creadas: int
    asignaciones: list[AsignacionReadWithAttributes]


class ClonarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    origen_contexto_id: uuid.UUID
    destino_contexto_id: uuid.UUID
    nuevo_desde: datetime
    nuevo_hasta: datetime | None = None


class ClonarResponse(BaseModel):
    clonadas: int
    asignaciones: list[AsignacionReadWithAttributes]


class ModificarVigenciaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    contexto_id: uuid.UUID
    nuevo_desde: datetime
    nuevo_hasta: datetime | None = None


class ModificarVigenciaResponse(BaseModel):
    modificadas: int
