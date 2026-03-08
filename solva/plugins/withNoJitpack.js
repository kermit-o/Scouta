const { withAppBuildGradle, withSettingsGradle } = require('@expo/config-plugins');

module.exports = function withNoJitpack(config) {
  // Step 1: Remove JitPack from settings.gradle
  config = withSettingsGradle(config, (config) => {
    config.modResults.contents = config.modResults.contents.replace(
      /maven\s*\{\s*url\s*['"]https:\/\/jitpack\.io['"]\s*\}/g,
      '// jitpack removed'
    );
    return config;
  });

  // Step 2: In app/build.gradle, force stripe versions AND exclude JitPack
  config = withAppBuildGradle(config, (config) => {
    let contents = config.modResults.contents;

    const block = `
configurations.all {
    resolutionStrategy {
        force 'com.stripe:stripe-android:22.7.4'
        force 'com.stripe:financial-connections:22.7.4'
        force 'com.stripe:payments-core:22.7.4'
        force 'com.stripe:payments-ui-core:22.7.4'
        force 'com.stripe:stripe-ui-core:22.7.4'
    }
    exclude group: 'com.jitpack'
}

repositories {
    exclusiveContent {
        forRepository { maven { url 'https://jitpack.io' } }
        filter { excludeGroupByRegex 'com\\.stripe.*' }
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
