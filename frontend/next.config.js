/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // 配置允许的图片域名（仅支持真实图片API）
    domains: [
      'images.unsplash.com',      // Unsplash API 图片
      'source.unsplash.com',      // Unsplash Source（备用）
      'images.pexels.com',        // Pexels API 图片
    ],
  },
}

module.exports = nextConfig
