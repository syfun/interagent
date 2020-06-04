from typing import Any, Type

from gql import field_resolver
from gql.parser import parse_info
from pydantic import BaseModel

from app.db import transaction


def decapitalize(s: str) -> str:
    return s[:1].lower() + s[1:]


class ResolverSet:
    model: Any
    resource: str
    create_schema_type: Type[BaseModel] = None
    update_schema_type: Type[BaseModel] = None
    filter_schema_type: Type[BaseModel] = None
    soft_delete: bool = False

    def resource_get(self):
        """SparePart => sparePart"""
        return decapitalize(self.resource)

    def resource_list(self):
        """SparePart => spareParts"""
        return decapitalize(self.resource) + 's'

    def resource_create(self):
        """SparePart => createSparePart"""
        return 'create' + self.resource

    def resource_update(self):
        """SparePart => updateSparePart"""
        return 'update' + self.resource

    def resource_delete(self):
        """SparePart => deleteSpareParts"""
        return 'delete' + self.resource + 's'

    def register(self):
        field_resolver('Mutation', self.resource_create())(self.create())
        field_resolver('Mutation', self.resource_update())(self.update())
        field_resolver('Mutation', self.resource_delete())(self.delete())
        field_resolver('Query', self.resource_get())(self.get())
        field_resolver('Query', self.resource_list())(self.list())

    def build_create_object(self, input: dict):
        return self.create_schema_type(**input) if input else None

    def create(self):
        @transaction
        async def create_(parent, info, input: dict):
            obj_in = self.build_create_object(input)
            if not obj_in:
                return None

            obj_id = await self.model.objects.create(obj_in)
            obj = await self.first(info, load_=True, id=obj_id)
            await self.after_create(obj_in, obj)
            return obj

        return create_

    async def after_create(self, obj_in: Any, obj: Any):
        pass

    def build_update_object(self, input: dict):
        return self.update_schema_type(**input) if input else None

    def build_update_filter_object(self, obj_in: Any):
        return self.filter_schema_type(id=obj_in.id)

    async def after_update(self, obj_in: Any, old_obj: Any, new_obj: Any):
        pass

    async def check_old_object(self, info, id: int):
        return None

    def update(self):
        @transaction
        async def update_(parent, info, input: dict):
            obj_in = self.build_update_object(input)
            if not obj_in:
                return None

            old_obj = await self.check_old_object(info, obj_in.id)
            filter_obj = self.build_update_filter_object(obj_in)
            await self.model.objects.filter_by_model(filter_obj).update(obj_in)

            new_obj = await self.first(info, load_=True, id=obj_in.id)
            await self.after_update(obj_in, old_obj, new_obj)
            return new_obj

        return update_

    def build_delete_filter_object(self, input: dict):
        return self.filter_schema_type(**input) if input else None

    def delete(self):
        @transaction
        async def delete_(parent, info, input: dict):
            filter_obj = self.build_delete_filter_object(input)
            if not filter_obj:
                return None

            q = self.model.objects.filter_by_model(filter_obj)
            if self.soft_delete:
                return await q.soft_delete()

            return await q.delete()

        return delete_

    def build_get_filter_object(self, **kwargs):
        if self.filter_schema_type is None:
            return None

        if self.soft_delete:
            kwargs['is_deleted'] = False
        return self.filter_schema_type(**kwargs) if kwargs else None

    async def first(self, info, load_: bool = False, **kwargs):
        filter_obj = self.build_get_filter_object(**kwargs)
        if not filter_obj:
            return None

        q = self.model.objects.filter_by_model(filter_obj)
        if load_:
            q.load(parse_info(info))
        return await q.first()

    def get(self):
        async def get_(parent, info, id: str):
            return await self.first(info, load_=True, id=int(id))

        return get_

    async def build_list_filter_object(self, **kwargs):
        if self.filter_schema_type is None:
            return None

        return self.filter_schema_type(**kwargs) if kwargs else None

    def build_order_by(self):
        return None

    def list(self):
        async def _list(parent, info, offset: int = None, limit: int = None, filter: dict = None):
            filter_obj = await self.build_list_filter_object(**(filter or {}))
            meta = parse_info(info, depth=3).get_sub_field('data')
            q = self.model.objects
            if filter_obj:
                q = q.filter_by_model(filter_obj)
            if offset:
                q = q.offset(offset)
            if limit:
                q = q.limit(limit)
            if order_by := self.build_order_by():
                q = q.order_by(order_by)
            q = q.load(meta)
            return {'data': await q.all(), 'total_count': await q.count()}

        return _list
