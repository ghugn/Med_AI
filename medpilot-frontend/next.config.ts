import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy AI / backend calls during development so the frontend
  // never hard-codes the AI service URL in client code.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://127.0.0.1:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
