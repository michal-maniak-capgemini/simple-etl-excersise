from typing import Any

import sqlalchemy as sa
from sqlalchemy import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.common.utils.logger import logger

Engine: Engine = sa.create_engine("sqlite:///backend/database/sqlite_database.db")
Session: sessionmaker[Session] = sessionmaker(bind=Engine)
Base: Any = declarative_base()


def create_tables() -> None:
    logger.info("Dropping all existing tables...")
    Base.metadata.drop_all(Engine)
    logger.info("Creating tables from scratch...")
    Base.metadata.create_all(Engine)
    logger.info(f"Database recreated with engine {Engine}")
