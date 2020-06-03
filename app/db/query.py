from collections import defaultdict
from inspect import isfunction
from itertools import chain
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Union

from gql.parser import FieldMeta
from pydantic import BaseModel
from sqlalchemy.orm import load_only
from sqlalchemy.orm.query import Query as BaseQuery
from sqlalchemy.sql import func, literal_column, operators, or_, select

from app.db import database as db
from app.db.utils import format_join_row

Operator = Callable[..., Any]
PARSER = Callable[[Any], Any]

OPERATOR_MAP: Dict[str, Operator] = {
    'eq': operators.eq,
    'lt': operators.lt,
    'le': operators.le,
    'gt': operators.gt,
    'ge': operators.ge,
    'in': operators.in_op,
    'is': operators.is_,
    'isnot': operators.isnot,
    'notin': operators.notin_op,
    'like': operators.like_op,
    'ilike': operators.ilike_op,
    'notlike': operators.notlike_op,
    'notilike': operators.notilike_op,
}


def like_parse(v: str) -> str:
    return f'%{v}%'


PARSER_MAP: Dict[str, PARSER] = {
    'like': like_parse,
    'ilike': like_parse,
    'notlike': like_parse,
    'notilike': like_parse,
}


class Query(BaseQuery):
    _primary_key = None

    def __init__(self, model):
        super().__init__(model)
        self.schema = getattr(model, '__schema__', None)
        self.joins = getattr(model, '__joins__', None)
        self.table = model.__table__
        self.relationships = model.__mapper__.relationships
        self.used_relationships = set()
        self.limit_ = None
        self.offset_ = None
        self.meta_ = None

    @property
    def primary_key(self):
        if self._primary_key is None:
            self._primary_key = self.table.primary_key.columns.values()[0]
        return self._primary_key

    def remove_unconsumed_columns(self, values: dict) -> dict:
        if not values:
            return values

        return {k: v for k, v in values.items() if k in self.table.c}

    def encode(self, data: Optional[Mapping], with_join: bool = True) -> Optional[BaseModel]:
        if not data:
            return None
        if with_join:
            data = format_join_row(data)
        return self.schema(**data)

    def iter_encode(self, data: List[Mapping]) -> Iterable[BaseModel]:
        return (self.encode(d) for d in data)

    def decode(self, obj_in: Union[dict, BaseModel]) -> Any:
        if isinstance(obj_in, dict):
            values = obj_in
        elif isinstance(obj_in, BaseModel):
            values = obj_in.dict(exclude_unset=True)
        else:
            raise RuntimeError(
                f'Query.decode expect dict or pydantic Model, but received {type(obj_in)}'
            )

        return self.remove_unconsumed_columns(values)

    async def create(self, obj_in: Union[dict, BaseModel]) -> Any:
        values = self.decode(obj_in)
        if not values:
            return None

        return await db.execute(self.table.insert(), values)

    async def create_many(self, obj_in: List[Union[dict, BaseModel]]) -> Any:
        if not obj_in:
            return None

        values = []
        for o in obj_in:
            value = self.decode(o)
            if value:
                values.append(value)
        return await db.execute_many(self.table.insert(), values)

    async def update(self, obj_in: Union[dict, BaseModel]) -> Any:
        values = self.decode(obj_in)
        if not values:
            return None

        await db.execute(self.table.update(whereclause=self.whereclause, values=values))

    async def delete(self):
        stmt = self.table.delete(whereclause=self.whereclause, returning=[self.primary_key])
        pk_name = self.primary_key.name
        return (r[pk_name] for r in await db.fetch_all(stmt))

    async def soft_delete(self):
        stmt = self.table.update(
            whereclause=self.whereclause, values=dict(is_deleted=True), returning=[self.primary_key]
        )
        pk_name = self.primary_key.name
        return (r[pk_name] for r in await db.fetch_all(stmt))

    async def get(self, pk: Any):
        stmt = self.lazy_build().filter(self.primary_key == pk).statement
        return self.encode(await db.fetch_one(stmt))

    async def all(self):
        q = self.lazy_build()
        q._limit = self.limit_
        q._offset = self.offset_
        return self.iter_encode(await db.fetch_all(q.statement))

    async def count(self):
        # TODO: maybe can optimize
        stmt = (
            self.execute_relationships()
            .options(load_only('id'))
            .from_self(func.count(literal_column('*')).label('count'))
            .statement
        )
        return await db.fetch_val(stmt)

    def lazy_build(self):
        return self.lazy_load().execute_relationships()

    async def first(self):
        return self.encode(await db.fetch_one(self.lazy_build().statement))

    def limit(self, limit):
        self.limit_ = limit
        return self

    def offset(self, offset):
        self.offset_ = offset
        return self

    def execute_relationships(self):
        q = self
        for relationship in self.used_relationships:
            q = q.join(relationship, isouter=not self.relationships[relationship].innerjoin)
        return q

    def compute_criterion(self, column: str, op: Operator, value: Any):
        args = column.split('__')
        if len(args) >= 2:
            relationship = self.relationships.get(args[0])
            if relationship is None:
                return None
            self.used_relationships.add(args[0])
            table = relationship.entity.local_table
            column = args[1]
        else:
            table = self.table

        return op(table.c[column], value)

    def filter_by_model(self, filter_obj: BaseModel):
        if filter_obj is None:
            return self

        values = filter_obj.dict(exclude_unset=True)
        criterions = []
        for k, v in values.items():
            extra = filter_obj.__fields__[k].field_info.extra
            op_name = extra.get('op', 'eq')
            op = OPERATOR_MAP.get(op_name)
            if not op:
                continue

            parser = extra.get('parser') or PARSER_MAP.get(op_name)
            v = parser(v) if parser and isfunction(parser) else v
            if op_name in {'like', 'ilike', 'notlike', 'notilike'}:
                columns = extra.get('columns') or [k]
                like_clauses = []
                for col in columns:
                    criterion = self.compute_criterion(col, op, v)
                    if criterion is not None:
                        like_clauses.append(criterion)
                criterion = or_(*like_clauses)
            else:
                criterion = self.compute_criterion(extra.get('column') or k, op, v)
            if criterion is not None:
                criterions.append(criterion)
        return self.filter(*criterions)

    def load(self, meta: FieldMeta):
        self.meta_ = meta
        return self

    def lazy_load(self):
        if not self.meta_:
            return self

        q = self.options(load_only(*[col for col in self.meta_.sections if col in self.table.c]))
        for name, sub_field in self.meta_.sub_fields.items():
            if not sub_field.sections or name not in self.relationships:
                continue
            self.used_relationships.add(name)
            table = self.relationships[name].entity.local_table
            q = q.add_columns(
                *[
                    table.c[col].label(name + '.' + col)
                    for col in sub_field.sections
                    if col in table.c
                ]
            )
        return q

    async def update_m2m(self, fk1: str, fk2: str, value1: Any, value2: List[Any]):
        """
        Example:
            ThingImage.objects.update_m2m(
                'thing_id',
                'image_id',
                thing_id,
                [image_id1, image_id2]
            )
        """
        if not value2:
            await db.execute(self.table.delete().where(self.table.c[fk1] == value1))
            return None

        stmt = select([self.table.c[fk2]]).where(self.table.c[fk1] == value1)
        data = await db.fetch_all(stmt)
        existed_value = set([r[fk2] for r in data])
        value2 = set(value2)
        new_value = value2.difference(existed_value)
        deleted_value = existed_value.difference(value2)

        if new_value:
            await self.create_many([{fk1: value1, fk2: v} for v in new_value])
        if deleted_value:
            await db.execute(
                self.table.delete()
                .where(self.table.c[fk1] == value1)
                .where(self.table.c[fk2].in_(deleted_value))
            )

    def _getattr(self, obj: Union[dict, BaseModel], item):
        return obj.get(item) if isinstance(obj, dict) else getattr(obj, item)

    async def update_m2m_more(
        self,
        old: List[Union[dict, BaseModel]],
        new: List[Union[dict, BaseModel]],
        fk1: str,
        fk2: str,
        update_fields: List[str] = None,
        update_existed: bool = True,
        delete_duplicated: bool = True,
    ) -> None:
        if not new:
            if old:
                await db.execute(
                    self.table.delete().where(
                        self.table.c[self.pk].in_([self._getattr(o, self.pk) for o in old])
                    )
                )
            return None

        if not old:
            if new:
                await self.create_many(new)
            return None

        pk_name = self.primary_key.name
        old_map = defaultdict(list)
        for obj in old:
            old_map[f'{self._getattr(obj, fk1)}:{self._getattr(obj, fk2)}'].append(
                self._getattr(obj, pk_name)
            )
        new_map = {f'{self._getattr(obj, fk1)}:{self._getattr(obj, fk2)}': obj for obj in new}
        old_map_keys, new_map_keys = set(old_map.keys()), set(new_map.keys())

        if create_keys := new_map_keys.difference(old_map_keys):
            await self.create_many([new_map[k] for k in create_keys])
        if delete_keys := old_map_keys.difference(new_map_keys):
            delete_pks = chain((old_map[k] for k in delete_keys))
            await db.execute(self.table.delete().where(self.table.c[self.pk].in_(delete_pks)))
        if delete_duplicated:
            pks = []
            for value in old_map.values():
                pks.extend(value[1:])
            if pks:
                await db.execute(self.table.delete().where(self.table.c[self.pk].in_(pks)))

        if (
            update_existed
            and update_fields
            and (update_keys := new_map_keys.intersection(old_map_keys))
        ):
            for key in update_keys:
                obj = new_map[key]
                stmt = (
                    self.table.update()
                    .where(self.table.c[fk1] == self._getattr(obj, fk1))
                    .where(self.table.c[fk2] == self._getattr(obj, fk2))
                )
                await db.execute(stmt, obj if isinstance(obj, dict) else obj.dict())
