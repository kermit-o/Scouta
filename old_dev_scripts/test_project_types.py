#!/usr/bin/env python3
"""
Verificar tipos de proyecto disponibles
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_project_types():
    """Verificar todos los tipos de proyecto"""
    try:
        from core.project_factory import ProjectType
        
        print("📋 TIPOS DE PROYECTO DISPONIBLES:")
        for project_type in ProjectType:
            print(f"   {project_type.value} -> {project_type.name}")
        
        print(f"\n🎯 NEXTJS_APP existe: {hasattr(ProjectType, 'NEXTJS_APP')}")
        if hasattr(ProjectType, 'NEXTJS_APP'):
            print(f"   Valor: {ProjectType.NEXTJS_APP.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_project_types()
