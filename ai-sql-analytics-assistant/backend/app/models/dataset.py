import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    table_name: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    row_count: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    column_count: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    columns: Mapped[list["ColumnMetadata"]] = relationship(  # noqa: F821
        "ColumnMetadata", back_populates="dataset", cascade="all, delete-orphan"
    )
    query_logs: Mapped[list["QueryLog"]] = relationship(  # noqa: F821
        "QueryLog", back_populates="dataset", cascade="all, delete-orphan"
    )
