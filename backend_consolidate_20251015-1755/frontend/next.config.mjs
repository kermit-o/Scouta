import path from "path";
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const nextConfig = {
  // En este stage, la raíz del workspace es el padre de /frontend
  outputFileTracingRoot: path.join(__dirname, ".."),
  experimental: { optimizePackageImports: [] }
};
export default nextConfig;
