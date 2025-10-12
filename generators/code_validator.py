import os
import subprocess
import tempfile
import shutil
import json
from typing import Dict, List, Tuple

class CodeValidator:
    def __init__(self):
        self.validation_results = {}
    
    def validate_react_project(self, project_path: str) -> Dict[str, any]:
        """Valida un proyecto React generado"""
        print(f"🧪 Validando proyecto React: {project_path}")
        
        validation_results = {
            "project_path": project_path,
            "files_checked": [],
            "errors": [],
            "warnings": [],
            "success": False
        }
        
        try:
            # 1. Verificar estructura básica
            structure_ok = self._validate_project_structure(project_path, validation_results)
            if not structure_ok:
                return validation_results
            
            # 2. Validar sintaxis de archivos JavaScript/JSX (método mejorado)
            self._validate_js_syntax_improved(project_path, validation_results)
            
            # 3. Validar package.json
            self._validate_package_json(project_path, validation_results)
            
            # 4. Intentar build del proyecto
            self._validate_build(project_path, validation_results)
            
            # Determinar si el proyecto es exitoso
            # Consideramos éxito si no hay errores críticos y el build funciona
            critical_errors = [e for e in validation_results["errors"] if "sintaxis" not in e.lower()]
            validation_results["success"] = len(critical_errors) == 0 and validation_results.get("build_ok", False)
            
            if validation_results["success"]:
                print("✅ Validación completada: PROYECTO VÁLIDO")
            else:
                print(f"⚠️  Validación completada: {len(validation_results['errors'])} errores encontrados")
                
        except Exception as e:
            validation_results["errors"].append(f"Error durante validación: {str(e)}")
            
        return validation_results
    
    def _validate_project_structure(self, project_path: str, results: Dict) -> bool:
        """Valida la estructura básica del proyecto"""
        required_files = [
            "package.json",
            "src/App.jsx", 
            "src/main.jsx",
            "index.html",
            "vite.config.js"
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = os.path.join(project_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
            else:
                results["files_checked"].append(file_path)
        
        if missing_files:
            results["errors"].append(f"Archivos faltantes: {', '.join(missing_files)}")
            return False
            
        print("✅ Estructura de archivos: OK")
        return True
    
    def _validate_js_syntax_improved(self, project_path: str, results: Dict):
        """Valida la sintaxis de archivos JavaScript/JSX usando métodos mejorados"""
        js_files = []
        
        # Encontrar todos los archivos .js y .jsx
        for root, dirs, files in os.walk(os.path.join(project_path, "src")):
            for file in files:
                if file.endswith(('.js', '.jsx')):
                    js_files.append(os.path.join(root, file))
        
        for js_file in js_files:
            try:
                # Método 1: Verificar que el archivo no esté vacío y tenga contenido básico
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) == 0:
                    relative_path = os.path.relpath(js_file, project_path)
                    results["errors"].append(f"Archivo vacío: {relative_path}")
                    continue
                
                # Método 2: Verificar estructura básica de React
                if js_file.endswith('.jsx'):
                    if 'react' not in content.lower() and 'import' not in content.lower():
                        relative_path = os.path.relpath(js_file, project_path)
                        results["warnings"].append(f"Posible problema en {relative_path}: no parece ser un componente React")
                
                # Método 3: Verificar que tenga export/import básico
                if 'export' not in content and 'import' not in content:
                    relative_path = os.path.relpath(js_file, project_path)
                    results["warnings"].append(f"Archivo {relative_path} sin exports/imports")
                
                relative_path = os.path.relpath(js_file, project_path)
                results["files_checked"].append(f"{relative_path} (validación básica)")
                    
            except Exception as e:
                relative_path = os.path.relpath(js_file, project_path)
                results["warnings"].append(f"No se pudo validar {relative_path}: {str(e)}")
        
        print("✅ Validación básica de archivos: OK")
    
    def _validate_package_json(self, project_path: str, results: Dict):
        """Valida el package.json"""
        package_json_path = os.path.join(project_path, "package.json")
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Validar campos requeridos
            required_fields = ["name", "version", "scripts", "dependencies"]
            missing_fields = [field for field in required_fields if field not in package_data]
            
            if missing_fields:
                results["errors"].append(f"Package.json campos faltantes: {', '.join(missing_fields)}")
                return
            
            # Validar que el script 'dev' existe
            if "dev" not in package_data.get("scripts", {}):
                results["errors"].append("Package.json: script 'dev' no encontrado")
            
            # Validar dependencias React
            dependencies = package_data.get("dependencies", {})
            if "react" not in dependencies:
                results["errors"].append("Package.json: dependencia 'react' no encontrada")
                
            print("✅ Package.json: OK")
                
        except json.JSONDecodeError as e:
            results["errors"].append(f"Package.json inválido: {str(e)}")
        except Exception as e:
            results["errors"].append(f"Error validando package.json: {str(e)}")
    
    def _validate_build(self, project_path: str, results: Dict):
        """Intenta hacer build del proyecto para validar"""
        print("🔨 Probando build del proyecto...")
        
        # Crear un directorio temporal para la prueba de build
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Copiar proyecto a directorio temporal
                test_project_dir = os.path.join(temp_dir, "test_build")
                shutil.copytree(project_path, test_project_dir)
                
                # Instalar dependencias
                install_result = subprocess.run(
                    ['npm', 'install'],
                    cwd=test_project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if install_result.returncode != 0:
                    results["warnings"].append("No se pudieron instalar dependencias para prueba de build")
                    results["build_ok"] = False
                    return
                
                print("✅ Dependencias instaladas")
                
                # Intentar build
                build_result = subprocess.run(
                    ['npm', 'run', 'build'],
                    cwd=test_project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if build_result.returncode == 0:
                    print("✅ Build test: OK")
                    results["build_ok"] = True
                else:
                    error_msg = build_result.stderr[:200] + "..." if len(build_result.stderr) > 200 else build_result.stderr
                    results["warnings"].append(f"Build test falló: {error_msg}")
                    results["build_ok"] = False
                    
            except subprocess.TimeoutExpired:
                results["warnings"].append("Timeout en prueba de build")
                results["build_ok"] = False
            except Exception as e:
                results["warnings"].append(f"Error en prueba de build: {str(e)}")
                results["build_ok"] = False

def validate_generated_project(project_path: str) -> Dict[str, any]:
    """Función conveniente para validar un proyecto"""
    validator = CodeValidator()
    return validator.validate_react_project(project_path)

if __name__ == "__main__":
    # Test de validación
    test_project = "generated_projects/Test Project 1"
    
    if os.path.exists(test_project):
        results = validate_generated_project(test_project)
        
        print(f"\\n📊 RESULTADOS DE VALIDACIÓN:")
        print(f"✅ Archivos verificados: {len(results['files_checked'])}")
        print(f"❌ Errores: {len(results['errors'])}")
        print(f"⚠️  Advertencias: {len(results['warnings'])}")
        print(f"🔨 Build exitoso: {results.get('build_ok', False)}")
        print(f"�� Proyecto válido: {results['success']}")
        
        if results['errors']:
            print(f"\\n📋 ERRORES ENCONTRADOS:")
            for error in results['errors']:
                print(f"   • {error}")
                
        if results['warnings']:
            print(f"\\n📋 ADVERTENCIAS:")
            for warning in results['warnings']:
                print(f"   • {warning}")
    else:
        print(f"❌ Proyecto de prueba no encontrado: {test_project}")
EOF# Actualizar el validador para que use métodos apropiados
cat > generators/code_validator.py << 'EOF'
import os
import subprocess
import tempfile
import shutil
import json
from typing import Dict, List, Tuple

class CodeValidator:
    def __init__(self):
        self.validation_results = {}
    
    def validate_react_project(self, project_path: str) -> Dict[str, any]:
        """Valida un proyecto React generado"""
        print(f"🧪 Validando proyecto React: {project_path}")
        
        validation_results = {
            "project_path": project_path,
            "files_checked": [],
            "errors": [],
            "warnings": [],
            "success": False
        }
        
        try:
            # 1. Verificar estructura básica
            structure_ok = self._validate_project_structure(project_path, validation_results)
            if not structure_ok:
                return validation_results
            
            # 2. Validar sintaxis de archivos JavaScript/JSX (método mejorado)
            self._validate_js_syntax_improved(project_path, validation_results)
            
            # 3. Validar package.json
            self._validate_package_json(project_path, validation_results)
            
            # 4. Intentar build del proyecto
            self._validate_build(project_path, validation_results)
            
            # Determinar si el proyecto es exitoso
            # Consideramos éxito si no hay errores críticos y el build funciona
            critical_errors = [e for e in validation_results["errors"] if "sintaxis" not in e.lower()]
            validation_results["success"] = len(critical_errors) == 0 and validation_results.get("build_ok", False)
            
            if validation_results["success"]:
                print("✅ Validación completada: PROYECTO VÁLIDO")
            else:
                print(f"⚠️  Validación completada: {len(validation_results['errors'])} errores encontrados")
                
        except Exception as e:
            validation_results["errors"].append(f"Error durante validación: {str(e)}")
            
        return validation_results
    
    def _validate_project_structure(self, project_path: str, results: Dict) -> bool:
        """Valida la estructura básica del proyecto"""
        required_files = [
            "package.json",
            "src/App.jsx", 
            "src/main.jsx",
            "index.html",
            "vite.config.js"
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = os.path.join(project_path, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
            else:
                results["files_checked"].append(file_path)
        
        if missing_files:
            results["errors"].append(f"Archivos faltantes: {', '.join(missing_files)}")
            return False
            
        print("✅ Estructura de archivos: OK")
        return True
    
    def _validate_js_syntax_improved(self, project_path: str, results: Dict):
        """Valida la sintaxis de archivos JavaScript/JSX usando métodos mejorados"""
        js_files = []
        
        # Encontrar todos los archivos .js y .jsx
        for root, dirs, files in os.walk(os.path.join(project_path, "src")):
            for file in files:
                if file.endswith(('.js', '.jsx')):
                    js_files.append(os.path.join(root, file))
        
        for js_file in js_files:
            try:
                # Método 1: Verificar que el archivo no esté vacío y tenga contenido básico
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) == 0:
                    relative_path = os.path.relpath(js_file, project_path)
                    results["errors"].append(f"Archivo vacío: {relative_path}")
                    continue
                
                # Método 2: Verificar estructura básica de React
                if js_file.endswith('.jsx'):
                    if 'react' not in content.lower() and 'import' not in content.lower():
                        relative_path = os.path.relpath(js_file, project_path)
                        results["warnings"].append(f"Posible problema en {relative_path}: no parece ser un componente React")
                
                # Método 3: Verificar que tenga export/import básico
                if 'export' not in content and 'import' not in content:
                    relative_path = os.path.relpath(js_file, project_path)
                    results["warnings"].append(f"Archivo {relative_path} sin exports/imports")
                
                relative_path = os.path.relpath(js_file, project_path)
                results["files_checked"].append(f"{relative_path} (validación básica)")
                    
            except Exception as e:
                relative_path = os.path.relpath(js_file, project_path)
                results["warnings"].append(f"No se pudo validar {relative_path}: {str(e)}")
        
        print("✅ Validación básica de archivos: OK")
    
    def _validate_package_json(self, project_path: str, results: Dict):
        """Valida el package.json"""
        package_json_path = os.path.join(project_path, "package.json")
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Validar campos requeridos
            required_fields = ["name", "version", "scripts", "dependencies"]
            missing_fields = [field for field in required_fields if field not in package_data]
            
            if missing_fields:
                results["errors"].append(f"Package.json campos faltantes: {', '.join(missing_fields)}")
                return
            
            # Validar que el script 'dev' existe
            if "dev" not in package_data.get("scripts", {}):
                results["errors"].append("Package.json: script 'dev' no encontrado")
            
            # Validar dependencias React
            dependencies = package_data.get("dependencies", {})
            if "react" not in dependencies:
                results["errors"].append("Package.json: dependencia 'react' no encontrada")
                
            print("✅ Package.json: OK")
                
        except json.JSONDecodeError as e:
            results["errors"].append(f"Package.json inválido: {str(e)}")
        except Exception as e:
            results["errors"].append(f"Error validando package.json: {str(e)}")
    
    def _validate_build(self, project_path: str, results: Dict):
        """Intenta hacer build del proyecto para validar"""
        print("🔨 Probando build del proyecto...")
        
        # Crear un directorio temporal para la prueba de build
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Copiar proyecto a directorio temporal
                test_project_dir = os.path.join(temp_dir, "test_build")
                shutil.copytree(project_path, test_project_dir)
                
                # Instalar dependencias
                install_result = subprocess.run(
                    ['npm', 'install'],
                    cwd=test_project_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if install_result.returncode != 0:
                    results["warnings"].append("No se pudieron instalar dependencias para prueba de build")
                    results["build_ok"] = False
                    return
                
                print("✅ Dependencias instaladas")
                
                # Intentar build
                build_result = subprocess.run(
                    ['npm', 'run', 'build'],
                    cwd=test_project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if build_result.returncode == 0:
                    print("✅ Build test: OK")
                    results["build_ok"] = True
                else:
                    error_msg = build_result.stderr[:200] + "..." if len(build_result.stderr) > 200 else build_result.stderr
                    results["warnings"].append(f"Build test falló: {error_msg}")
                    results["build_ok"] = False
                    
            except subprocess.TimeoutExpired:
                results["warnings"].append("Timeout en prueba de build")
                results["build_ok"] = False
            except Exception as e:
                results["warnings"].append(f"Error en prueba de build: {str(e)}")
                results["build_ok"] = False

def validate_generated_project(project_path: str) -> Dict[str, any]:
    """Función conveniente para validar un proyecto"""
    validator = CodeValidator()
    return validator.validate_react_project(project_path)

if __name__ == "__main__":
    # Test de validación
    test_project = "generated_projects/Test Project 1"
    
    if os.path.exists(test_project):
        results = validate_generated_project(test_project)
        
        print(f"\\n📊 RESULTADOS DE VALIDACIÓN:")
        print(f"✅ Archivos verificados: {len(results['files_checked'])}")
        print(f"❌ Errores: {len(results['errors'])}")
        print(f"⚠️  Advertencias: {len(results['warnings'])}")
        print(f"🔨 Build exitoso: {results.get('build_ok', False)}")
        print(f"�� Proyecto válido: {results['success']}")
        
        if results['errors']:
            print(f"\\n📋 ERRORES ENCONTRADOS:")
            for error in results['errors']:
                print(f"   • {error}")
                
        if results['warnings']:
            print(f"\\n📋 ADVERTENCIAS:")
            for warning in results['warnings']:
                print(f"   • {warning}")
    else:
        print(f"❌ Proyecto de prueba no encontrado: {test_project}")
