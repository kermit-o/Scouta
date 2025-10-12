# Leer el .env actual
with open('.env', 'r') as f:
    lines = f.readlines()

# Corregir las variables de Stripe
new_lines = []
stripe_fixed = False

for line in lines:
    if line.startswith('STRIPE_SECRET_KEY=') and 'pk_test' in line:
        # Esta es una clave pública en lugar de secreta - comentarla
        new_lines.append('# ' + line.strip() + '  # ❌ ESTA ES CLAVE PÚBLICA, NO SECRETA\n')
        new_lines.append('STRIPE_SECRET_KEY=sk_test_tu_clave_secreta_real_aqui\n')
        new_lines.append('STRIPE_PUBLISHABLE_KEY=' + line.split('=')[1])
        stripe_fixed = True
    elif line.startswith('STRIPE_WEBHOOK_SECRET=') and line.strip().endswith('fkO'):
        # Esta parece una clave secreta en webhook - corregir
        new_lines.append('# ' + line.strip() + '  # ❌ ESTO PARECE UNA CLAVE SECRETA\n')
        new_lines.append('STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret_real_aqui\n')
    else:
        new_lines.append(line)

# Si no se encontró Stripe, agregar configuración
if not stripe_fixed:
    new_lines.append('\n# Stripe Configuration\n')
    new_lines.append('STRIPE_SECRET_KEY=sk_test_tu_clave_secreta_real_aqui\n')
    new_lines.append('STRIPE_PUBLISHABLE_KEY=pk_test_tu_clave_publica_real_aqui\n')
    new_lines.append('STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret_real_aqui\n')

# Escribir el archivo corregido
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("✅ .env corregido - Variables de Stripe actualizadas")
print("📝 NECESITAS OBTENER CLAVES REALES DE stripe.com")
