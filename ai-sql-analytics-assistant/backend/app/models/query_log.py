import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prompt: Mapped[str] = mapped_column(sa.Text, nullable=False)
    generated_sql: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str] = mapped_column(
        sa.String(20), nullable=False
    )  # "success" | "safety_blocked" | "llm_error" | "execution_error"
    execution_time_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    result_row_count: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    cache_hit: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="query_logs")  # noqa: F821
