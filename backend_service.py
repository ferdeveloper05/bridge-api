#import os
import sys
import platform
import hashlib
import shutil
import subprocess
#import time 
from pathlib import Path


# ===================================
# 1. Servicio de Autenticacion (hashlib + pathlib)
# ===================================

class AuthService: 
    def __init__(self, base_dir: Path):
        self.db_file = base_dir / "databases" / "users.txt"
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_file.exists(): 
            self.db_file.touch()
    
    def _hash_password(self, password: str) -> str: 
        """ Convierte la contrasena en un hash sha256 """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    def register_user(self, username: str, password: str): 
        """ Registrar nuevo usuario con la contrasena hasheada """
        password_hash = self._hash_password(password=password)
        
        # Validar la existencia del usuario
        if self.db_file.exists(): 
            for line in self.db_file.read_text("utf-8").splitlines(): 
                print(line)
                if line: 
                    user_in_db, _ = line.split(':')
                    if user_in_db == username: 
                        print(f"❌ El usuario '{username}' ya existe.")
                        return False
        
        # Guardar credenciales 
        with open(self.db_file, 'a', encoding='utf-8') as file: 
            file.write(f'{username}:{password_hash}')
            
        print(f"✅ Usuario '{username}' registrado correctamente")
        return True
    
# ====================================
# 2. Servicio de Almacenamiento (pathlib + hashlib + shutil)
# ====================================

class StorageService: 
    def __init__(self, base_dir: Path):
        self.storage_dir = base_dir / "storage"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def _calculate_sha256(self, file_path: Path) -> Path:
        """ Calcula el hash de un archivo por bloques """ 
        hash_file = hashlib.sha256()
        with open(file_path, 'rb') as file: 
            while chunk := file.read(8192): 
                hash_file.update(chunk)
        return hash_file.hexdigest()
    
    def upload_document(self, source_file: Path, username: str) -> Path | None: 
        """ Mueve un archivo a la carpeta del usuario y genera su firma sha256 """
        if not source_file.exists() or not source_file.is_file(): 
            print(f"El archivo fuente {source_file} no exite")
            return None
        
        # Crea el directorio con el nombre del usuario
        user_dir = self.storage_dir / username
        user_dir.mkdir(exist_ok=True)
        
        # Crea un archivo dentro del directorio del usuario
        destination = user_dir / source_file.name
        shutil.copy2(source_file, destination)
        
        # Generar archivo de firma digital
        checksum = self._calculate_sha256(destination)
        hash_file = user_dir / f'{source_file.name}.sha256'
        hash_file.write_text(checksum, encoding='utf-8')
        
        print(f"📄 Archivo guardado en: {destination}")
        print(f"🔒 Firma SHA-256 generada: {checksum[:16]}...")

        return destination
    

# ===================================
# 3. Servicio de Auditoria y Sistema
# ===================================

class SystemAuditService: 
    @staticmethod
    def get_telemetry() -> dict: 
        """ Recopila informacion del sistema y prueba comando externos """
        v = sys.version_info
        
        # Probar que el subproceso 'ping' responde en el sistema operativo (SO)
        ping_cmd = ['ping', '-n', '1', '127.0.0.1'] if platform.system() == 'Windows' else ['ping', '-c', '1', '127.0.0.1']
        
        try: 
            result = subprocess.run(ping_cmd, check=False, capture_output=True, text=True, timeout=3)
            ping_status = "OK" if result.returncode == 0 else "FAILED"
        except Exception:  # noqa: BLE001
            ping_status = 'Error'
            
        return {
            'OS':platform.system(), 
            'Architecture': platform.architecture()[0], 
            'Python Version': f"{v.major}.{v.minor}.{v.micro}", 
            'Local looback ping': ping_status
        }
        
def main(): 
    base_dir = Path.cwd()
    
    auth_service = AuthService(base_dir=base_dir)
    storage_service = StorageService(base_dir=base_dir)
    
    print("Proyecto Integrador: BACKEND NATIVO")
    
    # 1.Prueba de Telemetria del servidor
    print('\n[1] Evaluando la telemetria del servidor...')
    telemetry = SystemAuditService.get_telemetry()
    for key, value in telemetry.items(): 
        print(f"  • {key}: {value}")
        
    # 2. Prueba de registro de usuario    
    print('\n[2] Pruebas de Registro de Usuario...')
    user = "admin_dev"
    auth_service.register_user(username=user, password="ClaveSuperSecreta01")
    
    # 3. Prueba de almacenaje temporal
    print('\n[3] Carga y Firma de Documento...')
    temp_file = Path.cwd() / "documento_prueba.txt"
    temp_file.write_text('Contenido confidencial del servidor en produccion.\nFecha: 2026', encoding='utf-8')
    
    storage_service.upload_document(source_file=temp_file, username=user)
    
    # Limpieza del archivo temporal de prueba
    if temp_file.exists() and temp_file.is_file(): 
        temp_file.unlink()
    

if __name__ == '__main__': 
    main()