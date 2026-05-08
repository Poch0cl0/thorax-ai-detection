"""user_roles appointments study.appointment_id

Revision ID: 8f9a12bc4d01
Revises: db6bb9240b23
Create Date: 2026-05-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f9a12bc4d01"
down_revision: Union[str, Sequence[str], None] = "db6bb9240b23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role", name="uq_user_roles_user_role"),
    )
    op.create_index(op.f("ix_user_roles_user_id"), "user_roles", ["user_id"], unique=False)

    conn = op.get_bind()
    conn.execute(sa.text("INSERT INTO user_roles (user_id, role) SELECT id, role FROM users"))

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("attending_user_id", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["attending_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_appointments_attending_user_id"),
        "appointments",
        ["attending_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_appointments_patient_id"), "appointments", ["patient_id"], unique=False
    )

    with op.batch_alter_table("studies", schema=None) as batch:
        batch.add_column(
            sa.Column("appointment_id", sa.Integer(), nullable=True),
        )
        batch.create_foreign_key(
            "fk_studies_appointment_id",
            "appointments",
            ["appointment_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch.create_index(batch.f("ix_studies_appointment_id"), ["appointment_id"])


def downgrade() -> None:
    with op.batch_alter_table("studies", schema=None) as batch:
        batch.drop_index(batch.f("ix_studies_appointment_id"))
        batch.drop_constraint("fk_studies_appointment_id", type_="foreignkey")
        batch.drop_column("appointment_id")

    op.drop_table("appointments")

    op.drop_index(op.f("ix_user_roles_user_id"), table_name="user_roles")
    op.drop_table("user_roles")
