from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- SCHEMAS DE USUARIOS (Historias #1 y #8) ---
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# --- SCHEMAS DE ANÁLISIS ---
class VulnerabilityRequest(BaseModel):
    text: str
    username: str  # El frontend enviará el usuario logueado aquí

class EntityBase(BaseModel):
    entity: str
    category: str
    start: int
    end: int

class AnalysisResponse(BaseModel):
    severity: str
    confidence_score: float
    entities: List[EntityBase]
    summary: str

# --- NUEVOS SCHEMAS PARA RF-08 (CRUD USUARIOS) ---
class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None

# --- NUEVOS SCHEMAS PARA RF-07 (AUDITORÍA) ---
class AuditLogResponse(BaseModel):
    id: int
    username: str
    original_text: str
    severity: str
    confidence_score: float
    entities_json: str
    summary: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# --- SCHEMAS PARA RF-06 (ESTADÍSTICAS DEL DASHBOARD) ---
class SeverityCount(BaseModel):
    Baja: int = 0
    Media: int = 0
    Alta: int = 0
    Critica: int = 0 # Usamos 'Critica' sin tilde para la clave del JSON

class DashboardStats(BaseModel):
    total_scans: int
    average_confidence: float
    severity_distribution: SeverityCount