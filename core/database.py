from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, MetaData, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings


metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_engine(settings.postgres_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class DocumentRecord(TimestampMixin, Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content_hash = Column(String(128), nullable=False, unique=True, index=True)
    metadata_json = Column(JSON, nullable=False, default=dict)


class SyncJob(TimestampMixin, Base):
    __tablename__ = "sync_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    records_read = Column(Integer, default=0, nullable=False)
    records_written = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=False, default=dict)


class AgentSession(TimestampMixin, Base):
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    state = Column(JSON, nullable=False, default=dict)


class ToolCall(TimestampMixin, Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), nullable=False, index=True)
    tool_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    input_json = Column(JSON, nullable=False, default=dict)
    output_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)


class AnalysisReport(TimestampMixin, Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    report_path = Column(String(1000), nullable=False)
    metadata_json = Column(JSON, nullable=False, default=dict)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
