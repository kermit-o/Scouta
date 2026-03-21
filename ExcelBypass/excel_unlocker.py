#!/usr/bin/env python3
"""
Excel Password Recovery Tool
-----------------------------
Intenta desbloquear archivos .xlsx protegidos con contraseña.
Soporta:
  1. Eliminar protección de hojas (sheet/workbook protection)
  2. Ataque por diccionario para archivos cifrados
  3. Fuerza bruta para contraseñas cortas (hasta N caracteres)

Uso:
  python excel_unlocker.py archivo.xlsx
  python excel_unlocker.py archivo.xlsx --wordlist mis_palabras.txt
  python excel_unlocker.py archivo.xlsx --bruteforce --max-len 4
"""

import sys
import os
import io
import argparse
import itertools
import string
import time
import shutil
from zipfile import ZipFile, BadZipFile
import xml.etree.ElementTree as ET

try:
    import msoffcrypto
    HAS_MSOFFCRYPTO = True
except ImportError:
    HAS_MSOFFCRYPTO = False
    print("⚠️  msoffcrypto-tool no instalado. Solo se eliminará protección de hojas.")
    print("   Instala con: pip install msoffcrypto-tool\n")

try:
    from openpyxl import load_workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ─────────────────────────────────────────────
#  1. DETECTAR TIPO DE PROTECCIÓN
# ─────────────────────────────────────────────

def detect_protection(filepath):
    """Devuelve (is_encrypted, has_sheet_protection)"""
    is_encrypted = False
    has_sheet_protection = False

    # ¿Está cifrado a nivel de archivo?
    if HAS_MSOFFCRYPTO:
        with open(filepath, "rb") as f:
            try:
                office_file = msoffcrypto.OfficeFile(f)
                is_encrypted = office_file.is_encrypted()
            except Exception:
                is_encrypted = False

    # ¿Tiene protección de hoja (sin cifrado)?
    if not is_encrypted:
        try:
            with ZipFile(filepath, 'r') as z:
                for name in z.namelist():
                    if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                        content = z.read(name).decode("utf-8", errors="ignore")
                        if "sheetProtection" in content or "workbookProtection" in content:
                            has_sheet_protection = True
                            break
        except BadZipFile:
            pass

    return is_encrypted, has_sheet_protection


# ─────────────────────────────────────────────
#  2. ELIMINAR PROTECCIÓN DE HOJAS (sin cifrado)
# ─────────────────────────────────────────────

def remove_sheet_protection(filepath, out_path):
    """
    Elimina las etiquetas <sheetProtection> y <workbookProtection>
    directamente del XML dentro del ZIP.
    """
    import re

    tmp = out_path + ".tmp.zip"
    modified = False

    with ZipFile(filepath, 'r') as zin, ZipFile(tmp, 'w') as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)

            if item.filename.startswith("xl/worksheets/") and item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                new_text = re.sub(r'<sheetProtection[^/]*/>', '', text)
                new_text = re.sub(r'<sheetProtection[^>]*>.*?</sheetProtection>', '', new_text, flags=re.DOTALL)
                if new_text != text:
                    modified = True
                data = new_text.encode("utf-8")

            elif item.filename == "xl/workbook.xml":
                text = data.decode("utf-8")
                new_text = re.sub(r'<workbookProtection[^/]*/>', '', text)
                new_text = re.sub(r'<workbookProtection[^>]*>.*?</workbookProtection>', '', new_text, flags=re.DOTALL)
                if new_text != text:
                    modified = True
                data = new_text.encode("utf-8")

            zout.writestr(item, data)

    if modified:
        shutil.move(tmp, out_path)
        return True
    else:
        os.remove(tmp)
        return False


# ─────────────────────────────────────────────
#  3. DESCIFRAR ARCHIVO CON CONTRASEÑA CONOCIDA
# ─────────────────────────────────────────────

def decrypt_with_password(filepath, password, out_path):
    """Descifra el archivo usando la contraseña dada. Devuelve True si éxito."""
    if not HAS_MSOFFCRYPTO:
        return False
    try:
        with open(filepath, "rb") as f:
            office_file = msoffcrypto.OfficeFile(f)
            if not office_file.is_encrypted():
                return False
            office_file.load_key(password=password)
            buf = io.BytesIO()
            office_file.decrypt(buf)
            buf.seek(0)
            with open(out_path, "wb") as out:
                out.write(buf.read())
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
#  4. ATAQUE POR DICCIONARIO
# ─────────────────────────────────────────────

COMMON_PASSWORDS = [
    "", "1234", "12345", "123456", "1234567", "12345678",
    "password", "pass", "excel", "admin", "qwerty",
    "abc123", "letmein", "welcome", "monkey", "dragon",
    "master", "hello", "secret", "test", "office",
    "empresa", "trabajo", "solva", "2023", "2024", "2025",
]

def dictionary_attack(filepath, out_path, wordlist_path=None):
    passwords = list(COMMON_PASSWORDS)

    if wordlist_path and os.path.exists(wordlist_path):
        print(f"📖 Cargando wordlist: {wordlist_path}")
        with open(wordlist_path, "r", errors="ignore") as f:
            passwords += [line.strip() for line in f if line.strip()]

    print(f"🔍 Probando {len(passwords)} contraseñas del diccionario...")
    for i, pwd in enumerate(passwords, 1):
        if i % 500 == 0:
            print(f"   ...{i}/{len(passwords)}")
        if decrypt_with_password(filepath, pwd, out_path):
            return pwd

    return None


# ─────────────────────────────────────────────
#  5. FUERZA BRUTA
# ─────────────────────────────────────────────

def bruteforce_attack(filepath, out_path, max_len=4, charset=None):
    if charset is None:
        charset = string.digits + string.ascii_lowercase

    total = sum(len(charset)**l for l in range(1, max_len + 1))
    print(f"💪 Fuerza bruta: charset={len(charset)} chars, max_len={max_len}")
    print(f"   Total combinaciones: {total:,}")
    print(f"   Puede tardar mucho para max_len > 4\n")

    count = 0
    start = time.time()

    for length in range(1, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            pwd = "".join(combo)
            count += 1
            if count % 10000 == 0:
                elapsed = time.time() - start
                rate = count / elapsed
                remaining = (total - count) / rate
                print(f"   {count:,}/{total:,}  ({rate:.0f}/s)  ETA: {remaining:.0f}s")
            if decrypt_with_password(filepath, pwd, out_path):
                return pwd

    return None


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Recuperar/desbloquear archivos Excel protegidos"
    )
    parser.add_argument("filepath", help="Ruta al archivo .xlsx")
    parser.add_argument("--output", "-o", help="Archivo de salida (default: desbloqueado_<original>)")
    parser.add_argument("--wordlist", "-w", help="Ruta a un archivo de palabras (una por línea)")
    parser.add_argument("--bruteforce", "-b", action="store_true", help="Activar fuerza bruta")
    parser.add_argument("--max-len", "-m", type=int, default=4, help="Longitud máxima para fuerza bruta (default: 4)")
    parser.add_argument("--password", "-p", help="Probar una contraseña específica")
    args = parser.parse_args()

    filepath = args.filepath
    if not os.path.exists(filepath):
        print(f"❌ Archivo no encontrado: {filepath}")
        sys.exit(1)

    base = os.path.basename(filepath)
    out_path = args.output or f"desbloqueado_{base}"

    print("=" * 55)
    print("  🔓 Excel Password Recovery Tool")
    print("=" * 55)
    print(f"  Archivo:  {filepath}")
    print(f"  Salida:   {out_path}")
    print("=" * 55 + "\n")

    # Detectar protección
    is_encrypted, has_sheet_prot = detect_protection(filepath)
    print(f"📊 Cifrado a nivel de archivo: {'SÍ' if is_encrypted else 'NO'}")
    print(f"📊 Protección de hoja/libro:   {'SÍ' if has_sheet_prot else 'NO'}\n")

    # ── Caso 1: Solo protección de hojas (sin cifrado) ──
    if not is_encrypted and has_sheet_prot:
        print("✅ El archivo NO está cifrado. Eliminando protección de hojas...")
        shutil.copy2(filepath, out_path)
        if remove_sheet_protection(out_path, out_path):
            print(f"\n✅ ¡Protección eliminada! Archivo guardado en: {out_path}")
        else:
            print("⚠️  No se encontraron etiquetas de protección para eliminar.")
        sys.exit(0)

    # ── Caso 2: Sin protección detectada ──
    if not is_encrypted and not has_sheet_prot:
        print("ℹ️  El archivo no parece estar protegido. Copiando tal cual...")
        shutil.copy2(filepath, out_path)
        print(f"   Guardado en: {out_path}")
        sys.exit(0)

    # ── Caso 3: Archivo cifrado ──
    if is_encrypted:
        if not HAS_MSOFFCRYPTO:
            print("❌ El archivo está cifrado pero msoffcrypto-tool no está instalado.")
            print("   Instala con: pip install msoffcrypto-tool")
            sys.exit(1)

        # Intentar con contraseña específica
        if args.password:
            print(f"🔑 Probando contraseña: '{args.password}'")
            if decrypt_with_password(filepath, args.password, out_path):
                print(f"✅ ¡Contraseña correcta! Archivo guardado en: {out_path}")
                sys.exit(0)
            else:
                print("❌ Contraseña incorrecta.")
                sys.exit(1)

        # Ataque por diccionario
        found = dictionary_attack(filepath, out_path, args.wordlist)
        if found is not None:
            print(f"\n✅ ¡Contraseña encontrada!: '{found}'")
            print(f"   Archivo guardado en: {out_path}")
            sys.exit(0)

        print("❌ Diccionario agotado sin éxito.\n")

        # Fuerza bruta (opcional)
        if args.bruteforce:
            print("🔨 Iniciando fuerza bruta...")
            found = bruteforce_attack(filepath, out_path, max_len=args.max_len)
            if found is not None:
                print(f"\n✅ ¡Contraseña encontrada!: '{found}'")
                print(f"   Archivo guardado en: {out_path}")
                sys.exit(0)
            else:
                print(f"\n❌ Fuerza bruta completada sin éxito (max_len={args.max_len}).")
                print("   Prueba aumentando --max-len o añade una wordlist más grande.")
        else:
            print("💡 Sugerencias:")
            print("   1. Si recuerdas pistas de la contraseña, crea un archivo wordlist.txt")
            print("      con posibles contraseñas (una por línea) y ejecuta:")
            print(f"      python excel_unlocker.py {filepath} -w wordlist.txt")
            print("   2. Para fuerza bruta (contraseñas cortas):")
            print(f"      python excel_unlocker.py {filepath} --bruteforce --max-len 4")
            print("   3. Si recuerdas la contraseña exacta:")
            print(f"      python excel_unlocker.py {filepath} -p \"tu_contraseña\"")


if __name__ == "__main__":
    main()