from sqlalchemy import Boolean, Column, DateTime, Enum as BaseEnum, Integer, TypeDecorator, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import expression

from .query import Query


def add_objects(query_cls):
    @hybrid_property
    def objects(cls):
        return query_cls(cls)

    def wrap(cls):
        cls.objects = objects

        return cls

    return wrap


@add_objects(Query)
class CustomBase:
    id = Column(Integer, primary_key=True)


class TimeMixin:
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(),
    )


class SoftDeleteMixin:
    is_deleted = Column('is_deleted', Boolean, nullable=False, server_default=expression.false())


class Enum(TypeDecorator):
    impl = BaseEnum

    def process_bind_param(self, value, dialect):
        return self.impl.enum_class(value)

    def process_result_value(self, value, dialect):
        return None if value is None else value.value


Base = declarative_base(cls=CustomBase)
