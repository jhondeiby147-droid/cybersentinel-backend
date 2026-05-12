import json
import re
from typing import List

# --- LIBRERÍAS DE TERCEROS ---
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session   # <-- Aquí estaba el error (faltaba Session)
from sqlalchemy import func

# --- IMPORTACIONES LOCALES ---
from app.schemas.schema import (
    VulnerabilityRequest, AnalysisResponse, 
    UserCreate, UserLogin, UserBase, 
    UserResponse, UserUpdate, AuditLogResponse,
    DashboardStats, SeverityCount    # <-- Faltaban los schemas del dashboard
)
from app.services.ai_service import ai_engine
from app.db.database import SessionLocal, AuditLog, User

router = APIRouter()

# ==========================================
# DEPENDENCIA DE BASE DE DATOS
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# MÓDULO DE USUARIOS (RF-01, RF-08 / Historias #1 y #8)
# ==========================================

@router.post("/users/register", response_model=UserBase)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    nuevo_usuario = User(username=user.username, password=user.password, role=user.role)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/users/login", response_model=UserBase)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    """Obtiene la lista de todos los usuarios registrados."""
    usuarios = db.query(User).all()
    return usuarios

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Actualiza el rol o la contraseña de un usuario existente."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if user_data.password:
        db_user.password = user_data.password # type: ignore
    if user_data.role:
        db_user.role = user_data.role # type: ignore
        
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Elimina un usuario del sistema."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_user)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}

# ==========================================
# MÓDULO DE ANÁLISIS (RF-02 a RF-05 / Historias #2, #3, #4, #5)
# ==========================================

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_vulnerability(request: VulnerabilityRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == request.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado. Debe iniciar sesión.")

    try:
        # Llamamos al motor mejorado
        result = ai_engine.analyze(request.text)

        # VALIDACIÓN DE SEGURIDAD EXTRA:
        # Si no hay entidades técnicas (IPs, Puertos) y el resumen es sospechoso,
        # bajamos la confianza para advertir al usuario en el Front.
        has_technical_data = any(e['category'] in ['IP_ADDRESS', 'PORT', 'LOC', 'ORG'] for e in result['entities'])
        
        if not has_technical_data and result['confidence_score'] > 0.5:
            result['confidence_score'] = 0.35 # Penalización por falta de evidencia física
            if "ERROR" not in result['summary']:
                result['summary'] = "(Análisis con baja evidencia técnica): " + result['summary']

        entities_str = json.dumps(result["entities"])

        nuevo_registro = AuditLog(
            username=request.username,
            original_text=request.text,
            severity=result["severity"],
            confidence_score=result["confidence_score"],
            entities_json=entities_str,
            summary=result["summary"]
        )

        db.add(nuevo_registro)
        db.commit()

        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")

# ==========================================
# MÓDULO DE AUDITORÍA Y DASHBOARD (RF-06, RF-07 / Historias #6 y #7)
# ==========================================

@router.get("/audit", response_model=List[AuditLogResponse])
async def get_audit_logs(db: Session = Depends(get_db)):
    """Obtiene el registro histórico de todas las peticiones procesadas."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return logs

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Calcula y devuelve métricas agregadas para el Dashboard."""
    total_scans = db.query(AuditLog).count()
    
    if total_scans == 0:
        return DashboardStats(
            total_scans=0,
            average_confidence=0.0,
            severity_distribution=SeverityCount()
        )
    
    avg_conf = db.query(func.avg(AuditLog.confidence_score)).scalar() or 0.0
    severities = db.query(AuditLog.severity, func.count(AuditLog.severity)).group_by(AuditLog.severity).all()
    
    sev_dict = {sev: count for sev, count in severities}
    
    return DashboardStats(
        total_scans=total_scans,
        average_confidence=round(avg_conf, 2),
        severity_distribution=SeverityCount(
            Baja=sev_dict.get("Baja", 0),
            Media=sev_dict.get("Media", 0),
            Alta=sev_dict.get("Alta", 0),
            Critica=sev_dict.get("Crítica", 0) or sev_dict.get("Critica", 0)
        )
    )