const fs = require("fs");
const p = require("path");
const f = p.join(__dirname, "..", "node_modules", "expo-router", "_ctx.web.js");
let c = fs.readFileSync(f, "utf8");
c = c.replace("process.env.EXPO_ROUTER_APP_ROOT", "'../../app'");
c = c.replace("process.env.EXPO_ROUTER_IMPORT_MODE", "'lazy'");
fs.writeFileSync(f, c);
console.log("patched");
