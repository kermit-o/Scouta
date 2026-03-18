const fs = require("fs");
const p = require("path");
const f = p.join(__dirname,"..","node_modules","expo-router","_ctx.web.js");
const c = "export const ctx = require.context(\n  './app',\n  true,\n  /^(?:./)(?!(?:(?:(?:.*\\+api)|(?:\\+middleware)|(?:\\+(html|native-intent)))).\\[tj\\]sx?$).*(?:.android|.ios|.native)?\\.[tj]sx?$/,\n  'lazy'\n);\n";
fs.writeFileSync(f,c);
console.log("patched");