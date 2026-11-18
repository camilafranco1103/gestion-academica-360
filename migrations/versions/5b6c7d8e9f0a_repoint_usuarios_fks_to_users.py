"""repoint legacy usuarios foreign keys to users

C-25 unified `usuarios` into `users`, and the models reference `users.id`,
but earlier migrations created these foreign keys against `usuarios.id`.
This repoints them so inserts made through the models stop violating them.

Revision ID: 5b6c7d8e9f0a
Revises: ebe686c23962
Create Date: 2026-11-18 14:40:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "5b6c7d8e9f0a"
down_revision: Union[str, Sequence[str], None] = "ebe686c23962"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, column) pairs whose foreign key pointed at usuarios.id
LEGACY_FKS: list[tuple[str, str]] = [
    ("acknowledgments_aviso", "usuario_id"),
    ("asignaciones", "user_id"),
    ("asignaciones", "responsable_id"),
    ("calificaciones", "importado_por"),
    ("comunicaciones", "enviado_por"),
    ("entradas_padron", "usuario_id"),
    ("facturas", "usuario_id"),
    ("liquidaciones", "usuario_id"),
    ("mensajes_internos", "remitente_id"),
    ("mensajes_internos", "destinatario_id"),
    ("reservas_evaluacion", "alumno_id"),
    ("resultados_evaluacion", "alumno_id"),
    ("slots_encuentro", "creado_por"),
    ("tareas", "asignado_a"),
    ("versiones_padron", "cargado_por"),
]


def _repoint(target_table: str) -> None:
    if op.get_bind().dialect.name == "sqlite":
        return  # SQLite cannot ALTER constraints; test schemas come from the models
    for table, column in LEGACY_FKS:
        name = f"{table}_{column}_fkey"
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, target_table, [column], ["id"])


def upgrade() -> None:
    """Point the legacy foreign keys at users.id."""
    _repoint("users")


def downgrade() -> None:
    """Point the foreign keys back at usuarios.id."""
    _repoint("usuarios")
