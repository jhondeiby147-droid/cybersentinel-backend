from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./cybersentinel.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TABLA DE USUARIOS (Historia de Usuario #8) ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Texto plano al no haber capa de seguridad
    role = Column(String)      # Analista, Gerente o Administrador

# --- TABLA DE AUDITORÍA (Historia de Usuario #7) ---
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True) # Guardamos el usuario que hizo la petición
    original_text = Column(String, nullable=False)
    severity = Column(String, index=True)
    confidence_score = Column(Float)
    entities_json = Column(String)
    summary = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)