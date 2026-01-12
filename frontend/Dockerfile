# 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 构建参数（用于传递环境变量）
ARG NEXT_PUBLIC_API_URL=http://localhost:18890

# 设置环境变量
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# 复制package文件
COPY package.json pnpm-lock.yaml* package-lock.json* yarn.lock* ./

# 安装依赖（优先使用pnpm，如果不存在则使用npm）
RUN if [ -f pnpm-lock.yaml ]; then \
        npm install -g pnpm && pnpm install; \
    elif [ -f yarn.lock ]; then \
        npm install -g yarn && yarn install; \
    else \
        npm install; \
    fi

# 复制源代码
COPY . .

# 创建 public 目录（如果不存在，Next.js 需要）
# 如果目录为空，创建一个占位符文件，确保 COPY 不会失败
RUN mkdir -p /app/public && \
    if [ ! "$(ls -A /app/public)" ]; then \
        touch /app/public/.gitkeep; \
    fi

# 构建应用
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm run build; \
    elif [ -f yarn.lock ]; then \
        yarn build; \
    else \
        npm run build; \
    fi

# 生产阶段
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 创建非root用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 复制 public 目录（已确保在 builder 阶段存在且不为空）
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# 复制 standalone 构建产物
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 设置正确的权限
RUN chown -R nextjs:nodejs /app

USER nextjs

# 暴露端口
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# 启动Next.js
CMD ["node", "server.js"]
