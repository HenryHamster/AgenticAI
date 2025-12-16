import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Disable ESLint during production builds (linting should be done in CI/dev)
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable type checking during builds (should be done in CI/dev)
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
