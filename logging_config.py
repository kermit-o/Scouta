"""
CONFIGURACIÓN DE LOGGING DETALLADO PARA FORGE SAAS
"""
import logging
import sys
from pathlib import Path

# Crear directorio de logs
Path("logs").mkdir(exist_ok=True)

def setup_detailed_logging():
    """Configurar logging detallado para todos los componentes"""
    
    # Formato común
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger principal de la aplicación
    main_logger = logging.getLogger('forge_saas')
    main_logger.setLevel(logging.DEBUG)
    
    # Handlers
    file_handler = logging.FileHandler('logs/application.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    main_logger.addHandler(file_handler)
    main_logger.addHandler(console_handler)
    
    # Loggers específicos
    components = ['database', 'api', 'ai', 'payments', 'generators']
    for component in components:
        comp_logger = logging.getLogger(f'forge_saas.{component}')
        comp_logger.setLevel(logging.DEBUG)
        
        comp_file_handler = logging.FileHandler(f'logs/{component}.log')
        comp_file_handler.setLevel(logging.DEBUG)
        comp_file_handler.setFormatter(formatter)
        
        comp_logger.addHandler(comp_file_handler)
    
    return main_logger

# Inicializar logging
logger = setup_detailed_logging()

if __name__ == "__main__":
    logger.info("✅ Sistema de logging configurado correctamente")
    logger.debug("Este es un mensaje de debug")
    logger.info("Este es un mensaje de info")
    logger.warning("Este es un mensaje de warning")
    logger.error("Este es un mensaje de error")
