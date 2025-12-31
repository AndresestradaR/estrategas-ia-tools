/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.dropi.co',
      },
      {
        protocol: 'https',
        hostname: 'ads-scraper-multimedia-prod.s3.amazonaws.com',
      },
      {
        protocol: 'https',
        hostname: '**.dropkiller.com',
      },
    ],
  },
}

module.exports = nextConfig
