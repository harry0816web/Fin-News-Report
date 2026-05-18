import type { NextConfig } from "next";

const BACKEND_API_URL =
  process.env.BACKEND_API_URL ??
  "https://fin-news-functions-evaud7duf0bddxby.japaneast-01.azurewebsites.net";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_API_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
