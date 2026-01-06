# 🚀 快速开始指南 - TravelPlanGPT

## 5分钟快速体验

### 第一步：克隆项目

```bash
git clone https://github.com/yourusername/Travel-GPT.git
cd Travel-GPT
```

### 第二步：配置API密钥

```bash
# 复制环境变量模板
cd backend
cp .env.example .env
```

编辑 `backend/.env`，至少需要添加：
```env
OPENAI_API_KEY=sk-your-key-here
```

💡 **获取OpenAI Key**: https://platform.openai.com/api-keys

### 第三步：启动项目

#### Windows用户
双击运行 `start.bat`

#### Mac/Linux用户
```bash
chmod +x start.sh
./start.sh
```

#### 或者手动启动

**终端1 - 后端**：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**终端2 - 前端**：
```bash
cd frontend
npm install
npm run dev
```

### 第四步：访问应用

🎨 **前端**: http://localhost:3000  
📡 **后端API**: http://localhost:8000  
📚 **API文档**: http://localhost:8000/docs

## 🎯 开始使用

1. 在首页填写旅行需求：
   - **目的地**：如"上海"
   - **天数**：2-3天
   - **预算**：2000-5000元
   - **偏好**：选择美食、文化等

2. 点击"生成行程"

3. 查看AI实时规划过程

4. 浏览完整的旅行行程！

## 📖 示例体验

点击首页的预设卡片快速体验：
- 🍜 **上海2天美食之旅**
- 🏔️ **成都周末户外放松**
- ⛩️ **京都3天文化体验**

## ⚡ 可选配置（增强功能）

为了获得更好的体验，可以添加这些API密钥到 `backend/.env`：

```env
# 搜索增强（免费1000次/月）
TAVILY_API_KEY=tvly-xxx

# 高质量图片（免费50次/小时）
UNSPLASH_ACCESS_KEY=xxx

# 天气信息（免费1000次/天）
OPENWEATHER_API_KEY=xxx
```

**获取链接**：
- Tavily: https://tavily.com
- Unsplash: https://unsplash.com/developers
- OpenWeather: https://openweathermap.org/api

## 🐛 遇到问题？

### 常见问题

**Q: 前端无法连接后端**  
A: 确保后端运行在 `http://localhost:8000`，检查防火墙设置

**Q: "Module not found" 错误**  
A: 运行 `npm install` (前端) 或 `pip install -r requirements.txt` (后端)

**Q: OpenAI API错误**  
A: 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确，确保有API额度

**Q: 图片无法加载**  
A: 添加 `UNSPLASH_ACCESS_KEY` 或忽略（会使用placeholder图片）

### 调试模式

查看后端日志：
```bash
cd backend
python main.py
# 日志会显示详细的API调用信息
```

查看前端控制台：
- 打开浏览器开发者工具 (F12)
- 查看 Console 标签

## 📚 下一步

- 阅读 [完整文档](README.md)
- 查看 [API文档](API.md)
- 了解 [部署指南](DEPLOYMENT.md)
- 参与 [贡献](CONTRIBUTING.md)

## 💬 需要帮助？

- 提交 Issue: https://github.com/yourusername/Travel-GPT/issues
- 查看 FAQ: [README.md#常见问题](README.md)

---

🎉 **享受你的AI旅行规划体验！**
