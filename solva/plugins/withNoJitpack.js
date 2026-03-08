const { withSettingsGradle } = require('@expo/config-plugins');

module.exports = function withNoJitpack(config) {
  return withSettingsGradle(config, (config) => {
    config.modResults.contents = config.modResults.contents.replace(
      /maven\s*\{\s*url\s*["']https:\/\/jitpack\.io["']\s*\}/g,
      '// jitpack removed'
    );
    return config;
  });
};
