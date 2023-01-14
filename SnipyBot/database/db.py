from __future__ import annotations

from typing import Union, Literal, TYPE_CHECKING
from typing_extensions import TypeAlias

import attrs
import asyncio

from datetime import datetime


from prisma.models import (
    User,
)
from prisma.models import Warn as PrismaWarn

from prisma import Prisma
from prisma.types import WarnUpdateInput

if TYPE_CHECKING:
    from prisma.types import (
        enums,
        UserCreateInput,
        UserOptionalCreateInput,
        UserUpdateInput,
        WarnCreateWithoutRelationsInput,
        WarnCreateInput,
        WarnUpdateManyMutationInput,
        WarnWhereInput,
        WarnWhereUniqueInput,
        WarnUpsertInput,
        WarnCountAggregateInput,
        WarnCountAggregateOutput,
        UserInclude,
        WarnInclude,
    )

    UserPayload: TypeAlias = Union[UserCreateInput, UserOptionalCreateInput]
    UserUpdatePayload: TypeAlias = UserUpdateInput
    WarnCreatePayload: TypeAlias = WarnCreateWithoutRelationsInput
    WarnUpdateManyPayload: TypeAlias = WarnUpdateManyMutationInput


__all__: tuple[str, ...] = (
    "Warn",
    "SnipyDatabase",
)


class WarnUpdatePayload(WarnUpdateInput):
    user_id: int
    server_id: int


@attrs.define(init=True, str=True, kw_only=True)
class Warn:
    id: str | None = None
    user_id: int
    moderator_id: int
    server_id: int
    expires_at: datetime | None = None
    reason: str | None = None


def check_connection(func):
    """
    A decorator to check if the object is connected, if not it raises a RuntimeError.

    This decorator is used only on methods that requires a connection to the database before
    doing something.
    """
    def decorator(self, *args, **kwargs):
        if not self._connected:
            raise RuntimeError(
                "Before trying to make a query you must connect to the database "
                "through the 'connect' method."
            )
        return func(self, *args, **kwargs)
    return decorator

def check_includes(func):
    """
    A decorator to check if only 'include_all' or 'include_partial' are passed, since setting
    those two parameters as True at the same time causes queries errors. 
    
    If the two parameters are both True it raises a ValueError. 
    """
    def decorator(self, *args, **kwargs):
        includes = kwargs.get("include_all", False), kwargs.get("include_partial", False)
        if sum(includes) not in {0, 1}:
            raise ValueError(f"You only one include parameter can be true:  you've passed {includes=!r}")
        return func(self, *args, **kwargs)
    return decorator


class SnipyDatabase:
    def __init__(self) -> None:
        self.database = Prisma()
        self._connected: bool = False
    
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        del self
    
    async def connect(self) -> None:
        if self._connected:
            raise RuntimeError("You're already connected to the database.")
        await self.database.connect()
        self._connected = True
    
    async def disconnect(self) -> None:
        await self.database.disconnect()
        self._connected = False
    
    @check_connection
    async def create_warn(
        self,
        *,
        user_id: int,
        moderator_id: int,
        server_id: int,
        expires_at: datetime | None = None,
        reason: str | None = None,
        include_all: bool = False,
        include_partial: bool = False,
    ) -> PrismaWarn | None:
        _warn_payload: WarnCreateInput = {
            "user": {
                "connect": {
                    "id": user_id
                }
            },
            "server": {
                "connect": {
                    "id": server_id
                }
            },
            "moderator_id": moderator_id
        }

        if expires_at and isinstance(expires_at, datetime):
            _warn_payload["expires_at"] = expires_at
        if reason:
            _warn_payload["reason"] = reason
        
        include_payload = self._warn_include_generator(
            include_all=include_all,
            include_partial=include_partial
        )

        return await self.database.warn.create(
            data=_warn_payload,
            include=include_payload
        )
    
    @check_connection
    async def delete_warn(
        self,
        *,
        warn_id: str,
        include_all: bool = False,
        include_partial: bool = False,
    ) -> PrismaWarn | None:
        include_payload = self._warn_include_generator(
            include_all=include_all,
            include_partial=include_partial
        )

        return await self.database.warn.delete(
            where={
                "id": warn_id
            },
            include=include_payload
        )
    
    @check_connection
    async def upsert(
        self,
        *,
        warn_id: str,
        warn_create: Warn,
        warn_update: Warn,
        include_all: bool = False,
        include_partial: bool = False,
    ) -> PrismaWarn:
        _upsert_warn_payload: WarnUpsertInput = {}  # type: ignore
        _upsert_warn_create_payload: WarnCreateInput = {
            "user_id": warn_create.user_id,
            "server_id": warn_create.server_id,
            "moderator_id": warn_create.moderator_id
        }
        if warn_create.expires_at:
            _upsert_warn_create_payload["expires_at"] = warn_create.expires_at
        if warn_create.reason:
            _upsert_warn_create_payload["reason"] = warn_create.reason
        
        _upsert_warn_update_payload: WarnUpdateInput = {
            "user": {
                "connect": {
                    "id": warn_update.user_id
                }
            },
            "server": {
                "connect": {
                    "id": warn_update.server_id
                }
            },
            "moderator_id": warn_update.moderator_id
        }
        if warn_update.expires_at:
            _upsert_warn_update_payload["expires_at"] = warn_update.expires_at
        if warn_update.reason:
            _upsert_warn_update_payload["reason"] = warn_update.reason

        _upsert_warn_payload["create"] = _upsert_warn_create_payload
        _upsert_warn_payload["update"] = _upsert_warn_update_payload
        
        include_payload = self._warn_include_generator(
            include_all=include_all,
            include_partial=include_partial
        )

        return await self.database.warn.upsert(
            where={
                "id": warn_id
            },
            data=_upsert_warn_payload,
            include=include_payload
        )
    
    @check_includes
    def _warn_include_generator(
        self,
        include_all: bool,
        include_partial: bool,
    ) -> WarnInclude:
        warn_include_payload: WarnInclude = {}

        if include_all:
            warn_include_payload.update(
                {
                    "server": {
                        "include": {
                            "server_settings": True,
                            "warns": True
                        }
                    },
                    "user": {
                        "include": {
                            "warns": True
                        }
                    }
                }
            )
        if include_partial:
            warn_include_payload.update(
                {
                    "server": True,
                    "user": True
                }
            )
        return warn_include_payload
    
    
    @check_connection
    async def update_warn(
        self,
        *,
        warn_id: str,
        user_id: int | None = None,
        disconnect_user: bool = False,
        moderator_id: int | None = None,
        server_id: int | None = None,
        disconnect_server: bool = False,
        expires_at: datetime | None = None,
        reason: str | None = None,
        include_all: bool = False,
        include_partial: bool = False,
    ) -> PrismaWarn | None:
        _warn_update_payload: WarnUpdateInput = {}
        
        if user_id:
            _warn_update_payload["user"] = {
                "connect": {
                    "id": user_id
                }
            }
            if disconnect_user:
                _warn_update_payload["user"] = {
                    "disconnect": True
                }
        if server_id:
            _warn_update_payload["server"] = {
                "connect": {
                    "id": server_id
                }
            }
            if disconnect_server:
                _warn_update_payload["server"] = {
                    "disconnect": True
                }
        
        if moderator_id:
            _warn_update_payload["moderator_id"] = moderator_id
        if expires_at:
            _warn_update_payload["expires_at"] = expires_at
        if reason:
            _warn_update_payload["reason"] = reason

        include_payload = self._warn_include_generator(
            include_all=include_all,
            include_partial=include_partial
        )
        return await self.database.warn.update(
            where={
                "id": warn_id
            },
            data=_warn_update_payload,
            include=include_payload
        )
    
    @check_connection
    async def create_many_warns(
        self,
        *,
        warns: list[Warn],
        skip_duplicates: bool = False
    ) -> int:
        _create_many_warn_payload: list[WarnCreatePayload] = []
        for warn in warns:
            _warn_payload: WarnCreatePayload = {
                "user_id": warn.user_id,
                "moderator_id": warn.moderator_id,
                "server_id": warn.server_id,
            }

            if warn.expires_at:
                _warn_payload["expires_at"] = warn.expires_at
            if warn.reason:
                _warn_payload["reason"] = warn.reason
            
            _create_many_warn_payload.append(_warn_payload)

        return await self.database.warn.create_many(
            data=_create_many_warn_payload,
            skip_duplicates=skip_duplicates
        )
    
    @check_connection
    async def update_many_warns(
        self,
        *,
        where: WarnWhereInput | None = None,
        moderator_id: int | None = None,
        expires_at: datetime | None = None,
        reason: str | None = None,
    ) -> int:
        _update_many_warn_payload: WarnUpdateManyPayload = {}

        if moderator_id:
            _update_many_warn_payload["moderator_id"] = moderator_id
        if expires_at:
            _update_many_warn_payload["expires_at"] = expires_at
        if reason:
            _update_many_warn_payload["reason"] = reason

        return await self.database.warn.update_many(
            where=where or {},  # {} updates all the warns
            data=_update_many_warn_payload
        )

    @check_connection
    async def delete_many_warns(
        self,
        *,
        where: WarnWhereInput | None = None
    ) -> int:
        return await self.database.warn.delete_many(
            where=where
        )
    
    @check_connection
    async def count_warns(
        self,
        *,
        select: WarnCountAggregateInput | None = None,
        limit: int | None = None,
        offset: int | None = None,
        where: WarnWhereInput | None = None,
        warn_id_for_cursor: str | None = None,
    ) -> WarnCountAggregateOutput | int:
        _cursor_payload: WarnWhereUniqueInput = {}  # type: ignore
        if warn_id_for_cursor:
            _cursor_payload["id"] = warn_id_for_cursor

        return await self.database.warn.count(
            select=select,
            take=limit,
            skip=offset,
            where=where,
            cursor=_cursor_payload
        )

    # TODO:
    # - implement warn queries
    # - implement user queries
    # - implement all server operations

    @check_connection
    async def update_user(
        self,
        *,
        user_id: int,
        nickname: str | None = None,
        nicknames: list[str] | None = None,
        warns: list[Warn] | None = None,
        role: enums.Role | None = None,
        include_warns: bool = False,
        include_all: bool = False,
        include_partial: bool = False,
    ) -> User | None:
        _user_update_payload: UserUpdatePayload = {}
        if nickname:
            _user_update_payload["nickname"] = nickname
        if nicknames:
            _user_update_payload["nicknames"] = nicknames
        if role and isinstance(role, enums.Role):
            _user_update_payload["role"] = role
        
        if warns:
            for warn in warns:
                if warn.user_id != user_id:
                    raise ValueError("The 'user_id' linked to the Warn model must be equal to the provided 'user_id'")
                
                # if no Id is provided on the Warn object it's not possible to update
                # a warn (since the Id is the Unique constraint) so we use the short circuit
                # and skip to the next iteration
                if warn.id is None:
                    continue

                _warn_update_payload: WarnUpdatePayload = {
                    "user_id": warn.user_id,
                    "server_id": warn.server_id,
                    "moderator_id": warn.moderator_id,
                }

                if warn.reason is not None:
                    _warn_update_payload["reason"] = warn.reason
                if warn.expires_at is not None:
                    _warn_update_payload["expires_at"] = warn.expires_at
                
                # Update warns
                await self.database.warn.update(
                    where={
                        "id": warn.id
                    },
                    data=_warn_update_payload
                )
        
        include_payload: UserInclude = {}
        if not include_warns:
            include_payload = self._user_include_generator(
                include_all=include_all,
                include_partial=include_partial
            )
        if include_warns:
            include_payload["warns"] = True

        # update the user
        return await self.database.user.update(
            where={
                "id": user_id
            },
            data=_user_update_payload,
            include=include_payload
        )
    
    @check_includes
    def _user_include_generator(
        self,
        include_all: bool,
        include_partial: bool,
        ) -> UserInclude:
            include_payload: UserInclude = {}

            if include_partial:
                include_payload["warns"] = {
                    "include": {
                        "server": True,
                        "user": True
                    }
                }
            if include_all:
                include_payload["warns"] = {
                    "include": {
                        "server": {
                            "include": {
                                "server_settings": True,
                                "warns": True
                            }
                        },
                        "user": True
                    }
                }
            return include_payload
    
    @check_connection
    async def delete_user(
        self,
        *,
        user_id: int,
        include_warns: bool = False,
        include_partial: bool = False,
        include_all: bool = False,
    ) -> User | None:
        include_payload = {}
        if not include_warns:
            include_payload: UserInclude = self._user_include_generator(
                include_all=include_all,
                include_partial=include_partial
            )

        if include_warns:
            include_payload["warns"] = True

        return await self.database.user.delete(
            where={
                "id": user_id
            },
            include=include_payload
        )

    @check_connection
    async def create_user(
        self,
        *,
        user_id: int,
        nickname: str,
        nicknames: list[str] | None = None,
        warns: list[Warn] | None = None,
        role: enums.Role | None = None,
        include_warns: bool = False,
        include_partial: bool = False,
        include_all: bool = False,
    ) -> User | None:
        user_payload: UserPayload = {
            "id": user_id,
            "nickname": nickname,
        }

        if role and isinstance(role, enums.Role):
            user_payload["role"] = role
        
        if nicknames:
            user_payload["nicknames"] = nicknames
        
        # Create the user
        await self.database.user.create(
            data=user_payload
        )
        
        _warns_payload: list[WarnCreatePayload] = []
        if warns:
            for warn in warns:
                if warn.user_id != user_id:
                    raise ValueError("The 'user_id' linked to the Warn model must be equal to the provided 'user_id'")
                _warn: WarnCreatePayload = {
                    "user_id": warn.user_id,
                    "server_id": warn.server_id,
                    "moderator_id": warn.moderator_id,
                }

                if warn.reason is not None:
                    _warn["reason"] = warn.reason
                if warn.expires_at is not None:
                    _warn["expires_at"] = warn.expires_at
                
                _warns_payload.append(_warn)

        # Create warns
        await self.database.warn.create_many(
            data=_warns_payload
        )

        include_payload: UserInclude = {}
        if not include_warns:
            include_payload = self._user_include_generator(
                include_all=include_all,
                include_partial=include_partial
            )
        
        if include_warns:
            include_payload["warns"] = True

        # refetch user with linked warns (with linked server and user)
        return await self.database.user.find_unique(
            where={
                "id": user_id
            },
            include=include_payload
        )

async def main():
    async with SnipyDatabase() as db:
        user = await db.delete_user(
            user_id=72,
        )
    print(user.json(indent=2))

asyncio.run(main())