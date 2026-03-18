const fs = require("fs");
const path = require("path");
const file = path.join(__dirname, "..", "node_modules", "expo-router", "_ctx.web.js");
const fixed = "export const ctx = require.context(\n  '../../app',\n  true,\n  /^(?:\\.\\/)(?!(?:(?:(?:.*\\+api)|(?:\\+middleware)|(?:\\+(html|native-intent))))\\.[tj]sx?$).*(?:\\.android|\\.ios|\\.native)?\\.[tj]sx?$/,\n  'lazy'\n);\n";
fs.writeFileSync(file, fixed);
console.log("patched");