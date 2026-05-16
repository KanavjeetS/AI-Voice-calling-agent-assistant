/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  async rewrites() {
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    return [{ source: "/api/backend/:path*", destination: `${apiBase}/api/v1/:path*` }];
  }
};

export default nextConfig;
