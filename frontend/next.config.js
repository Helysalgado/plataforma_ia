/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Environment variables available on client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000',
  },
  
  // Image optimization
  images: {
    domains: ['localhost', 'bioai.ccg.unam.mx'],
  },
  
  // Disable x-powered-by header
  poweredByHeader: false,
}

module.exports = nextConfig
