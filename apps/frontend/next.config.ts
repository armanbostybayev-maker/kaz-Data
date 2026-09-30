import type { NextConfig } from "next";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
const staticMode = process.env.NEXT_PUBLIC_STATIC_MODE === "true";
const config: NextConfig = {
  output: staticMode ? "export" : "standalone",
  trailingSlash: staticMode,
  basePath,
  assetPrefix: basePath || undefined,
  images: { unoptimized: true },
};
export default config;
