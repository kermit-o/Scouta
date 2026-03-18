
const fs = require('fs');
const original = fs.readFileSync(require('path').join(__dirname, '../node_modules/expo-router/_ctx.web.js'), 'utf8');
const fixed = original.replace('process.env.EXPO_ROUTER_APP_ROOT', "'../app'").replace('process.env.EXPO_ROUTER_IMPORT_MODE', "'lazy'");
fs.writeFileSync(require('path').join(__dirname, '../node_modules/expo-router/_ctx.web.js'), fixed);
console.log('patched');
