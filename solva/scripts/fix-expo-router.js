const fs = require('fs')
const path = require('path')
const filePath = path.join(__dirname, '..', 'node_modules', 'expo-router', '_ctx.web.js')
const content = `export const ctx = require.context(
  '../../app',
  true,
  /^(?:\\.\\/)(?!(?:(?:(?:.*\\+api)|(?:\\+middleware)|(?:\\+(html|native-intent))))\\.\\[tj\\]sx?$).*(?:\\.android|\\.ios|\\.native)?\\.[tj]sx?$/,
  'lazy'
);
`
fs.writeFileSync(filePath, content)
console.log('✅ expo-router patched')
