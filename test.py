import asyncio
from prisma import Prisma
from prisma.types import enums


async def main() -> None:
    prisma = Prisma()
    await prisma.connect()
    """
    CREATE A USER + A WARN AND CONNECT THEM EACH OTHERS
    i still need to write wrapper for these dicts to make things easier, it would be something like

    create_user(
        id=...,
        nickname=...,
    )
    create_warn(
        user=user.id,  #this should be handled as connection (eg: i need to use the 'connect')
        server=server.id
        moderator_id=...,  #this is a normal field
        reason=...,
    )

    user = await prisma.user.create(
        data={
            "id": 10,
            "nickname": "Snipy",
        },
    )
    warn = await prisma.warn.create(
        data={
            "user": {
                "connect": {
                    "id": 10
                }
            },
            "server": {
                "connect": {
                    "id": 0
                }
            },
            "moderator_id": 69,
            "reason": "Lmao"
        }
    )
    servers = await prisma.server.find_many()
    print(servers)
    users = await prisma.user.find_many()
    print(users)
    await prisma.warn.create_many(
        data=
            [{
                'server_id': 0,
                'user_id': 10,
                'moderator_id': 2,
                'reason': 'lmao'
            }]
    )
    warn = await prisma.warn.find_unique(
        where={
            "user_id": 10,
            "server_id": 0
        },
        include={
            "server": True,
            "user": True
        }
    )
    print(warn)
    """
    "8c10fb7f-e57f-48a7-b123-cf625beddab5"
    user = await prisma.user.find_unique(
        where={
            'id': 72
        },
        include={}
    )
    print(user.json(indent=2))

    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())