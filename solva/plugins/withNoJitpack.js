const { withAppBuildGradle, withSettingsGradle, withProjectBuildGradle } = require('@expo/config-plugins');

module.exports = function withNoJitpack(config) {
  // Bloquear JitPack en settings.gradle (dependencyResolutionManagement)
  config = withSettingsGradle(config, (config) => {
    let contents = config.modResults.contents;
    
    // Remover jitpack de repositories
    contents = contents.replace(
      /maven\s*\{\s*url\s*["']https:\/\/jitpack\.io["']\s*\}/g,
      '// jitpack removed'
    );
    
    // Añadir bloqueo explícito en dependencyResolutionManagement si existe
    if (contents.includes('dependencyResolutionManagement')) {
      contents = contents.replace(
        'dependencyResolutionManagement {',
        `dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)`
      );
    }
    
    config.modResults.contents = contents;
    return config;
  });

  // Bloquear en root build.gradle con allprojects
  config = withProjectBuildGradle(config, (config) => {
    let contents = config.modResults.contents;
    
    const block = `
allprojects {
    configurations.all {
        resolutionStrategy {
            force "com.stripe:stripe-android:22.7.4"
            force "com.stripe:financial-connections:22.7.4"
            force "com.stripe:payments-core:22.7.4"
            force "com.stripe:payments-ui-core:22.7.4"
            force "com.stripe:stripe-ui-core:22.7.4"
        }
    }
    repositories {
        remove maven { url "https://jitpack.io" }
    }
}
`;
    if (!contents.includes('allprojects') || !contents.includes('jitpack')) {
      contents = contents + block;
    }
    
    config.modResults.contents = contents;
    return config;
  });

  return config;
};
EOFcd /workspaces/Scouta/solva

cat > plugins/withNoJitpack.js << 'EOF'
const { withAppBuildGradle, withSettingsGradle, withProjectBuildGradle } = require('@expo/config-plugins');

module.exports = function withNoJitpack(config) {
  // Bloquear JitPack en settings.gradle (dependencyResolutionManagement)
  config = withSettingsGradle(config, (config) => {
    let contents = config.modResults.contents;
    
    // Remover jitpack de repositories
    contents = contents.replace(
      /maven\s*\{\s*url\s*["']https:\/\/jitpack\.io["']\s*\}/g,
      '// jitpack removed'
    );
    
    // Añadir bloqueo explícito en dependencyResolutionManagement si existe
    if (contents.includes('dependencyResolutionManagement')) {
      contents = contents.replace(
        'dependencyResolutionManagement {',
        `dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)`
      );
    }
    
    config.modResults.contents = contents;
    return config;
  });

  // Bloquear en root build.gradle con allprojects
  config = withProjectBuildGradle(config, (config) => {
    let contents = config.modResults.contents;
    
    const block = `
allprojects {
    configurations.all {
        resolutionStrategy {
            force "com.stripe:stripe-android:22.7.4"
            force "com.stripe:financial-connections:22.7.4"
            force "com.stripe:payments-core:22.7.4"
            force "com.stripe:payments-ui-core:22.7.4"
            force "com.stripe:stripe-ui-core:22.7.4"
        }
    }
    repositories {
        remove maven { url "https://jitpack.io" }
    }
}
`;
    if (!contents.includes('allprojects') || !contents.includes('jitpack')) {
      contents = contents + block;
    }
    
    config.modResults.contents = contents;
    return config;
  });

  return config;
};
