const fs = require("fs");
const p = require("path");
const target = p.join(__dirname, "..", "node_modules", "expo-router", "_ctx.web.js");

// Contenido original del paquete npm con regex correcta
const original = `export const ctx = require.context(\n  process.env.EXPO_ROUTER_APP_ROOT,\n  true,\n  /^(?:\\.\\/)(?!(?:(?:(?:.*\\+api)|(?:\\+middleware)|(?:\\+(html|native-intent))))\\.[tj]sx?$).*(?:\\.android|\\.ios|\\.native)?\\.[tj]sx?$/,\n  process.env.EXPO_ROUTER_IMPORT_MODE\n);\n`;

// Solo reemplazar las variables de entorno, preservando el regex
const fixed = original
  .replace("process.env.EXPO_ROUTER_APP_ROOT", "'../app'")
  .replace("process.env.EXPO_ROUTER_IMPORT_MODE", "'lazy'");

fs.writeFileSync(target, fixed);
console.log("patched:", fs.readFileSync(target, "utf8").split("\n")[1].trim());
