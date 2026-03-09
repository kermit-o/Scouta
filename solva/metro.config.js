const { getDefaultConfig } = require('expo/metro-config')

const config = getDefaultConfig(__dirname)

// Excluye módulos nativos de Stripe en web
const { resolver } = config
const originalBlockList = resolver.blockList || []

config.resolver.resolverMainFields = ['react-native', 'browser', 'main']

module.exports = config
