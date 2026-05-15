import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class ColumnMetadata(Base):
    __tablename__ = "column_metadata"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    column_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    pg_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)   # e.g. "BIGINT", "TEXT"
    pandas_dtype: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    is_nullable: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    sample_values: Mapped[str | None] = mapped_column(sa.Text, nullable=True)  # JSON string
    ordinal_position: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="columns")  # noqa: F821
