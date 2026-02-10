#!/usr/bin/env python3
import os
import time

PROJECT_ID = "89d62a26-32dd-4f86-9c40-9a4f9770a5aa"
PROJECT_DIR = f"generated_projects/{PROJECT_ID}"

def watch_files():
    print(f"👀 MONITOREANDO ARCHIVOS EN TIEMPO REAL: {PROJECT_DIR}")
    print("=" * 60)
    
    last_files = set()
    
    for i in range(30):  # Monitorear por 30 ciclos
        if os.path.exists(PROJECT_DIR):
            current_files = set()
            for root, dirs, files in os.walk(PROJECT_DIR):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), PROJECT_DIR)
                    current_files.add(rel_path)
            
            new_files = current_files - last_files
            if new_files:
                print(f"\n🆕 Nuevos archivos detectados (ciclo {i+1}):")
                for file in sorted(new_files):
                    print(f"   📄 {file}")
                last_files = current_files
            else:
                print(f"⏳ Ciclo {i+1}: Esperando nuevos archivos... ({len(current_files)} archivos total)")
                
            # Si hay archivos, mostrar algunos importantes
            if current_files:
                important = [f for f in current_files if any(ext in f.lower() for ext in 
                            ['.md', 'package.json', '.js', '.jsx', '.ts', '.tsx', '.html', '.css'])]
                if important and i % 5 == 0:  # Mostrar cada 5 ciclos
                    print("   📋 Archivos importantes:")
                    for imp in sorted(important)[:5]:
                        print(f"      📄 {imp}")
        else:
            print(f"⏳ Ciclo {i+1}: Directorio no creado aún...")
        
        time.sleep(2)  # Verificar cada 2 segundos
    
    # Resumen final
    print(f"\n🎯 RESUMEN FINAL:")
    if os.path.exists(PROJECT_DIR):
        all_files = []
        for root, dirs, files in os.walk(PROJECT_DIR):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), PROJECT_DIR)
                all_files.append(rel_path)
        
        print(f"📊 Total de archivos generados: {len(all_files)}")
        print(f"📂 Estructura completa:")
        for file in sorted(all_files):
            print(f"   📄 {file}")
    else:
        print("❌ No se generaron archivos")

if __name__ == "__main__":
    watch_files()
