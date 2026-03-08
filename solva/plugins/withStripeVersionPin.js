const { withAppBuildGradle } = require('@expo/config-plugins');

module.exports = function withStripeVersionPin(config) {
  return withAppBuildGradle(config, (config) => {
    const forceBlock = `
configurations.all {
    resolutionStrategy {
        force 'com.stripe:stripe-android:22.7.4'
    }
}
`;
    if (!config.modResults.contents.includes('configurations.all')) {
      config.modResults.contents = config.modResults.contents.replace(
        'dependencies {',
        forceBlock + '\ndependencies {'
      );
    }
    return config;
  });
};
