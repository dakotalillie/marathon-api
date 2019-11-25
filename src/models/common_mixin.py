from datetime import datetime

from sqlalchemy import func, sql, text
from sqlalchemy.dialects.postgresql import UUID

from ..db import DB


class CommonMixin:
    id = DB.Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    created_at = DB.Column(DB.DateTime, nullable=False, server_default=func.now())
    updated_at = DB.Column(
        DB.DateTime, nullable=False, server_default=func.now(), onupdate=datetime.now,
    )
    is_active = DB.Column(
        DB.Boolean, nullable=False, server_default=sql.expression.true()
    )
