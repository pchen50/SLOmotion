"""repopulating movies

Revision ID: 7c8dc4beba56
Revises: 9c05649dfc2f
Create Date: 2025-05-28 20:55:13.552545

"""
from typing import Sequence, Union
from sqlalchemy import table, column, String, Integer

from alembic import op
import sqlalchemy as sa
import csv
import os


# revision identifiers, used by Alembic.
revision: str = '7c8dc4beba56'
down_revision: Union[str, None] = '9c05649dfc2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    movies_table = table(
        "movies",
        column("name", String),
        column("genre", String),
        column("year", Integer)
    )
    base_dir = os.path.dirname("newyearimdbmovies.csv")
    csv_path = os.path.join(base_dir, "newyearimdbmovies.csv")
    with open(csv_path, "r", newline="") as file:
        reader = csv.DictReader(file)
        rows = []
        for row in reader:
            rows.append({"name": row["name"], "genre": row["genre"], "year": row["year"]})
    op.bulk_insert(movies_table, rows)


def downgrade() -> None:
    """Downgrade schema."""
    connect = op.get_bind()
    connect.execute(
        sa.text(
            """
            TRUNCATE movies RESTART IDENTITY CASCADE
            """
        )
    )
