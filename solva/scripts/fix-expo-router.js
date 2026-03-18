const fs = require('fs')
const path = require('path')
const filePath = path.join(__dirname, '..', 'node_modules', 'expo-router', '_ctx.web.js')
const content = "export const ctx = require.context(\n  '../../app',\n  true,\n  /^\\.\\//,\n  'lazy'\n);\n"
fs.writeFileSync(filePath, content)
console.log('patched')
