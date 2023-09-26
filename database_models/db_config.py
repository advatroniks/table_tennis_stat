from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, async_scoped_session

from asyncio import current_task


class DataBaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    def get_async_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task
        )

        return session

    def get_scoped_session_dependency(self) -> AsyncSession:
        print("Session Began")
        session = self.get_async_scoped_session()

        yield session

        print("Session Closed")
        session.close()


db_helper = DataBaseHelper(
    url="postgresql+asyncpg://tikhon:123@localhost/sqlalchemy",
    echo=True
)