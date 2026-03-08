const { withSettingsGradle, withAppBuildGradle } = require('@expo/config-plugins');

// Remove JitPack and force Stripe from Maven Central
module.exports = function withNoJitpack(config) {
  return withAppBuildGradle(config, (config) => {
    let contents = config.modResults.contents;
    
    // Pin all stripe deps and exclude jitpack lookups
    const forceBlock = `
configurations.all {
    resolutionStrategy {
        force 'com.stripe:stripe-android:22.7.4'
        force 'com.stripe:financial-connections:22.7.4'
        force 'com.stripe:payments-core:22.7.4'
        force 'com.stripe:payments-ui-core:22.7.4'
        force 'com.stripe:stripe-ui-core:22.7.4'
    }
}
`;
    if (!contents.includes('resolutionStrategy')) {
      contents = contents.replace('dependencies {', forceBlock + '\ndependencies {');
    }
    config.modResults.contents = contents;
    return config;
  });
};
