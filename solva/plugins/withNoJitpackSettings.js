const { withSettingsGradle } = require('@expo/config-plugins');

module.exports = function withNoJitpackSettings(config) {
  return withSettingsGradle(config, (config) => {
    // Remove jitpack.io from repositories
    config.modResults.contents = config.modResults.contents.replace(
      /maven\s*\{\s*url\s*['"]https:\/\/jitpack\.io['"]\s*\}/g,
      '// jitpack removed'
    );
    return config;
  });
};
