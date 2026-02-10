#!/usr/bin/env python3
"""
Fix SQLAlchemy imports in all model files
"""
import os

models_dir = "database/models"

# Lista de tipos SQLAlchemy comunes que podrían faltar
required_imports = {
    'Boolean': 'Boolean',
    'Column': 'Column',
    'Integer': 'Integer', 
    'String': 'String',
    'Float': 'Float',
    'Text': 'Text',
    'DateTime': 'DateTime',
    'ForeignKey': 'ForeignKey',
    'JSON': 'JSON',
    'relationship': 'relationship',
    'func': 'func',
}

for filename in os.listdir(models_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        filepath = os.path.join(models_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Verificar qué imports están presentes
        imports_line = ''
        for line in content.split('\n'):
            if line.startswith('from sqlalchemy'):
                imports_line = line
                break
        
        print(f"\n=== {filename} ===")
        print(f"Current import: {imports_line}")
        
        # Verificar qué tipos se usan en el archivo
        used_types = []
        for sql_type, _ in required_imports.items():
            if sql_type in content and sql_type not in imports_line:
                used_types.append(sql_type)
        
        if used_types:
            print(f"Missing imports: {used_types}")
            
            # Agregar los imports faltantes
            if imports_line:
                # Modificar línea existente
                new_import = imports_line.replace('import ', f'import {", ".join(used_types)}, ')
                content = content.replace(imports_line, new_import)
            else:
                # Agregar nueva línea de import
                content = f'from sqlalchemy import {", ".join(used_types)}\n' + content
            
            # Escribir archivo corregido
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"✅ Fixed: added {used_types}")
        else:
            print("✅ No missing imports")
