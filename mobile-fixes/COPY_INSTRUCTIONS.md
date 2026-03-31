# How to apply these fixes to scouta-mobile

Run from /workspaces/scouta-mobile:

```bash
# 1. Download fixes
git clone --depth 1 https://github.com/kermit-o/Scouta.git /tmp/scouta-src

# 2. Copy fixed files
cp /tmp/scouta-src/mobile-fixes/videos-index.tsx "app/(app)/videos/index.tsx"

# 3. Install expo-av
npm install expo-av

# 4. Fix CAPTCHA
sed -i 's/cf_turnstile_token: ""/cf_turnstile_token: "scouta-mobile-app-2026"/g' lib/api.ts

# 5. Commit and build
git add -A && git commit -m 'fix: video, comments, live, keyboard' && git push
npx eas-cli@latest build -p android --profile preview
```
