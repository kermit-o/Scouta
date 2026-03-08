const { withAppBuildGradle, withSettingsGradle } = require('@expo/config-plugins');

module.exports = function withNoJitpack(config) {
  config = withSettingsGradle(config, (config) => {
    config.modResults.contents = config.modResults.contents.replace(
      /maven\s*\{\s*url\s*['"]https:\/\/jitpack\.io['"]\s*\}/g,
      '// jitpack removed'
    );
    return config;
  });

  config = withAppBuildGradle(config, (config) => {
    let contents = config.modResults.contents;

    const block = `
configurations.all {
    resolutionStrategy {
        force "com.stripe:stripe-android:22.7.4"
        force "com.stripe:financial-connections:22.7.4"
        force "com.stripe:payments-core:22.7.4"
        force "com.stripe:payments-ui-core:22.7.4"
        force "com.stripe:stripe-ui-core:22.7.4"
    }
}
`;
    if (!contents.includes('resolutionStrategy')) {
      contents = contents.replace('dependencies {', block + '\ndependencies {');
    }
    config.modResults.contents = contents;
    return config;
  });

  return config;
};
