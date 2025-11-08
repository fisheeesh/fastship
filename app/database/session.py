from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

engine = create_engine(
    url="sqlite:///shipment.db",
    echo=True,
    connect_args={"check_same_thread": False},
)


def create_db_tables():
    from .models import Shipment  # noqa: F401

    SQLModel.metadata.create_all(bind=engine)


def get_session():
    with Session(bind=engine) as session:
        yield session
