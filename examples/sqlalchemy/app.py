import asyncio

from emmett55 import App, Pipe, current
from emmett55.tools import service
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Thing(Base):
    __tablename__ = "things"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __json__(self):
        return {"id": self.id, "name": self.name}


engine = create_async_engine("sqlite+aiosqlite:///data.db")
db_session = async_sessionmaker(engine, expire_on_commit=False)


async def _setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with db_session() as session:
        async with session.begin():
            session.add_all([Thing(name="foo"), Thing(name="bar"), Thing(name="baz")])


class DBPipe(Pipe):
    async def open(self):
        sess = db_session()
        current.db = await sess.__aenter__()

    async def close(self):
        await current.db.__aexit__(None, None, None)

    async def on_pipe_success(self):
        await current.db.commit()

    async def on_pipe_failure(self):
        await current.db.rollback()


app = App(__name__)
app.pipeline = [DBPipe()]


@app.route()
@service.json
async def things():
    rv = {"data": []}
    res = await current.db.execute(select(Thing))
    for row in res.all():
        rv["data"].append(row[0].__json__())
    return rv


@app.command("setup")
def cmd_setup():
    asyncio.run(_setup_db())
