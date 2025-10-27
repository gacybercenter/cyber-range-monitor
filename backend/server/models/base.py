from typing import Final

import inflect
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, declared_attr

NAMING_CONVENTIONS = {
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}
SQLITE_UTC_FUNC: Final[str] = "datetime('now', 'utc')"
_inflect_engine = inflect.engine()


class MappedBase(DeclarativeBase):
    __abstract__ = True

    metadata = sa.MetaData(naming_convention=NAMING_CONVENTIONS)

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return _inflect_engine.plural(cls.__name__.lower())  # type: ignore[return]
