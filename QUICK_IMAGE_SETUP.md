# 🚀 快速配置真实图片（10分钟）

## 为什么要配置？

- ❌ **不配置**：显示彩色占位图 + 文字，体验一般
- ✅ **配置后**：真实的埃菲尔铁塔、故宫、富士山照片，专业高质量

---

## 选择一个 API（或两个都配置）

### 方案 A：Unsplash（推荐首选）⭐⭐⭐⭐⭐

**优点**：数百万专业旅行照片，质量最高  
**缺点**：50次/小时限制  
**时间**：5分钟

#### 步骤：
1. 打开 https://unsplash.com/developers
2. 点击 **Join Free** 注册（可用 Google 快速登录）
3. 点击 **New Application**
4. 填写：
   - Name: `Travel-GPT`
   - Description: `AI travel planner`
   - 勾选确认框
5. 创建后，复制 **Access Key**（长字符串）
6. 打开 `backend/.env` 文件，添加：
   ```env
   UNSPLASH_ACCESS_KEY=你复制的Access_Key
   ```

### 方案 B：Pexels（完全免费）⭐⭐⭐⭐⭐

**优点**：完全免费，200次/小时，无限月限额  
**缺点**：覆盖略少于 Unsplash  
**时间**：3分钟

#### 步骤：
1. 打开 https://www.pexels.com/api/
2. 点击 **Get Started**
3. 注册账号（可用 Google 快速登录）
4. 登录后自动显示 **API Key**
5. 复制 API Key
6. 打开 `backend/.env` 文件，添加：
   ```env
   PEXELS_API_KEY=你复制的API_Key
   ```

### 方案 C：两个都配置（最佳）⭐⭐⭐⭐⭐

**优点**：覆盖99%景点，互为备份  
**时间**：8-10分钟

按上面两个步骤都做一遍，在 `.env` 中同时添加两个 key。

---

## 测试配置

```bash
cd backend
python test_image_api.py
```

**成功输出示例**：
```
✅ UNSPLASH_ACCESS_KEY: abc123...xyz
✅ 成功找到 3 张图片
✅ 已配置 Unsplash + Pexels 双 API（最佳配置）
```

---

## 立即查看效果

1. 启动项目：`start.bat`（Windows）或 `./start.sh`（Linux/Mac）
2. 访问 http://localhost:3000
3. 生成一个旅行计划
4. 看到真实的景点照片！🎉

---

## 遇到问题？

查看详细指南：[IMAGE_API_GUIDE.md](IMAGE_API_GUIDE.md)

---

⏱️ **总耗时**：不到10分钟  
💰 **费用**：完全免费  
🎯 **效果**：从占位图 → 专业摄影作品
