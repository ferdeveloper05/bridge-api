from fastapi import APIRouter, Depends, Header, HTTPException

from backend_service import SystemAuditService

router = APIRouter(
    prefix="/system",
    responses={404: {"description": "Not found"}},
)


def autenticar_usuario_header(x_user_token: str = Header(...)): 
    if x_user_token != "token_admin_2026": 
        raise HTTPException(status_code=401, detail="Token no autorizado")
    
    return x_user_token


@router.get("/telemetry", summary="Obtener telemetría del sistema", description="Retorna la telemetría del sistema operativo y ejecuta diagnósticos con subprocess.", tags=["Sistema"])
def read_telemetry(token: str = Depends(autenticar_usuario_header)):
    """Retorna la telemetría del sistema operativo y ejecuta diagnósticos con subprocess."""
    return SystemAuditService.get_telemetry()


