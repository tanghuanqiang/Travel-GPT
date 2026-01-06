# 贡献指南

感谢你考虑为 TravelPlanGPT 做出贡献！

## 如何贡献

### 报告Bug
1. 确认bug未被报告过
2. 创建新的 Issue
3. 详细描述问题（环境、步骤、期望、实际）
4. 附上截图或错误日志

### 提交功能请求
1. 创建 Issue，标记为 "enhancement"
2. 描述功能需求和使用场景
3. 说明为什么这个功能有用

### Pull Request流程
1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交代码 (`git commit -m 'Add some AmazingFeature'`)
4. Push到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 代码规范

### 前端 (TypeScript/React)
- 使用 TypeScript strict模式
- 遵循 React Hooks最佳实践
- 组件使用函数式组件
- 使用 Tailwind CSS类名
- ESLint检查通过

### 后端 (Python)
- 遵循 PEP 8规范
- 使用类型注解
- Docstring使用Google风格
- 函数名使用snake_case
- 类名使用PascalCase

### Git Commit消息
- 使用清晰的commit消息
- 格式：`type: description`
- 类型：`feat`, `fix`, `docs`, `style`, `refactor`, `test`

示例：
```
feat: add weather API integration
fix: resolve image loading issue
docs: update README with deployment guide
```

## 开发环境设置

```bash
# 克隆你的fork
git clone https://github.com/your-username/Travel-GPT.git
cd Travel-GPT

# 添加上游仓库
git remote add upstream https://github.com/original/Travel-GPT.git

# 安装依赖
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
```

## 测试

运行测试前请确保：
- 所有依赖已安装
- 环境变量已配置
- 本地服务正常运行

## 行为准则

- 尊重他人
- 接受建设性批评
- 关注对社区最有利的事情
- 对新手友好

## 问题？

如有疑问，请创建 Issue 或联系维护者。

再次感谢你的贡献！🎉
