const { withAppBuildGradle } = require('@expo/config-plugins');

module.exports = function withNoGoogleServices(config) {
  return withAppBuildGradle(config, (config) => {
    config.modResults.contents = config.modResults.contents.replace(
      'apply plugin: "com.google.gms.google-services"',
      '// apply plugin: "com.google.gms.google-services" // disabled'
    );
    return config;
  });
};
