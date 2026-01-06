# 图片 API 获取指南 📸

本项目使用 **Unsplash** 和 **Pexels** 两个免费 API 来获取真实的旅行景点照片。

---

## 🎨 为什么需要真实图片？

- ❌ **之前**：使用占位图或随机图片，用户体验差
- ✅ **现在**：真实的景点、餐厅、酒店照片，专业高质量

---

## 📋 快速对比

| API | 免费限额 | 图片质量 | 注册难度 | 推荐指数 |
|-----|---------|---------|---------|---------|
| **Unsplash** | 50次/小时 | ⭐⭐⭐⭐⭐ | 简单 | ⭐⭐⭐⭐⭐ |
| **Pexels** | 200次/小时 | ⭐⭐⭐⭐⭐ | 简单 | ⭐⭐⭐⭐⭐ |

**建议**：两个都配置，互为备份，覆盖99%的旅行景点！

---

## 1️⃣ Unsplash API（强烈推荐）

### 为什么选择 Unsplash？
- 📚 **数百万张**专业旅行摄影作品
- 🏔️ **覆盖全球**热门景点、餐厅、酒店
- 🆓 **完全免费**，注册即可使用
- 🚀 **高质量**，图片美观专业

### 获取步骤

#### ① 注册账号
1. 访问：https://unsplash.com/
2. 点击右上角 **Join** 注册（可用邮箱或Google账号）
3. 验证邮箱

#### ② 创建开发者应用
1. 访问开发者页面：https://unsplash.com/developers
2. 点击 **Register as a developer**
3. 阅读并接受 **API Guidelines**

#### ③ 创建新应用
1. 点击 **New Application**
2. 填写应用信息：
   ```
   Application name: Travel-GPT
   Description: AI travel planning assistant that uses Unsplash to display real destination photos
   ```
3. 勾选确认框：
   - ✅ I agree to the API Use and Attribution guidelines
   - ✅ 其他确认项
4. 点击 **Create application**

#### ④ 获取 Access Key
1. 在应用详情页找到 **Keys** 部分
2. 复制 **Access Key**（以 `<YOUR_ACCESS_KEY>` 开头的长字符串）
   ```
   示例：ABC123xyz789...（实际约43个字符）
   ```

#### ⑤ 配置到项目
在 `backend/.env` 文件中添加：
```env
UNSPLASH_ACCESS_KEY=你的_Access_Key
```

### 免费限额
- **开发测试**：50 requests/hour
- **申请提升**：填写申请表可提升到 5,000 requests/hour（生产环境）

### 使用示例
```python
# 搜索"埃菲尔铁塔"的照片
from app.image_search import search_unsplash

images = search_unsplash("Eiffel Tower Paris landmark", count=3)
print(images)  # 返回3个高质量图片URL
```

### Attribution 要求
- 必须在图片附近显示摄影师姓名和 Unsplash 链接
- 简单文字即可：`Photo by [Photographer] on Unsplash`
- 项目已在前端自动添加 attribution

---

## 2️⃣ Pexels API（完全免费）

### 为什么选择 Pexels？
- 🆓 **完全免费**，无限请求（合理使用）
- 🌍 **全球景点**覆盖优秀
- 📷 **Curated 精选**，质量有保障
- 🔄 **完美备份**，与 Unsplash 互补

### 获取步骤

#### ① 注册账号
1. 访问：https://www.pexels.com/
2. 点击右上角 **Join** 注册
3. 验证邮箱

#### ② 获取 API Key
1. 访问 API 页面：https://www.pexels.com/api/
2. 点击 **Get Started** 或 **Your API Key**
3. 如果已登录，直接显示 API Key
4. 复制 **API Key**（一串长字符串）

#### ③ 配置到项目
在 `backend/.env` 文件中添加：
```env
PEXELS_API_KEY=你的_API_Key
```

### 免费限额
- **每小时**：200 requests
- **每月**：20,000 requests
- **完全免费**，无需信用卡

### 使用示例
```python
# 搜索"大皇宫曼谷"的照片
from app.image_search import search_pexels

images = search_pexels("Grand Palace Bangkok", count=3)
print(images)  # 返回3个真实照片URL
```

### Attribution 要求
- 推荐但非必需
- 显示：`Photo by [Photographer] on Pexels`

---

## 🚀 完整配置示例

### backend/.env 文件
```env
# ============= LLM 配置 =============
LLM_API_KEY=your_dashscope_key

# ============= 图片服务配置 =============
# Unsplash API（推荐首选）
UNSPLASH_ACCESS_KEY=你的_Unsplash_Access_Key

# Pexels API（完全免费备份）
PEXELS_API_KEY=你的_Pexels_API_Key

# ============= 其他可选服务 =============
TAVILY_API_KEY=your_tavily_key
```

---

## 🧪 测试 API 是否配置成功

### 方法1：在后端测试
```bash
cd backend
python -c "from app.image_search import search_unsplash, search_pexels; print(search_unsplash('paris', 1)); print(search_pexels('paris', 1))"
```

**成功输出**：
```
✅ Unsplash 找到 1 张图片: paris
['https://images.unsplash.com/...']
✅ Pexels 找到 1 张图片: paris
['https://images.pexels.com/...']
```

**失败输出**：
```
⚠️  未设置 UNSPLASH_ACCESS_KEY，请访问 https://unsplash.com/developers 获取
[]
```

### 方法2：运行项目测试
1. 启动后端：`cd backend && python run_server.py`
2. 生成一个旅行计划
3. 查看行程卡片是否显示真实景点照片

---

## 📊 工作原理

### 图片获取流程
```
用户请求生成行程
    ↓
LLM 生成景点列表
    ↓
调用 image_search.py
    ↓
① 优先搜索 Unsplash（高质量专业照片）
    ↓
② 如果结果不足，补充 Pexels
    ↓
③ 如果都失败，使用占位图
    ↓
返回3张图片URL给前端展示
```

### 搜索关键词优化
- **中文景点**：`"故宫 北京 landmark travel"`
- **英文景点**：`"Eiffel Tower Paris landmark"`
- **餐厅**：`"Sushi restaurant Tokyo interior"`
- **酒店**：`"Grand hotel room Shanghai"`

### 图片尺寸
- **Unsplash**：`regular` 尺寸（约1080px宽）
- **Pexels**：`large` 尺寸（适合网页显示）
- **前端显示**：自动适应卡片容器

---

## 🔍 常见问题

### Q1: 我只配置了 Unsplash，会怎样？
A: 可以正常使用！Pexels 作为备用，当 Unsplash 结果不够时才调用。

### Q2: 两个都不配置会怎样？
A: 会显示占位图（彩色背景 + 景点名称文字），功能不受影响但美观度下降。

### Q3: 搜索中文景点能找到图片吗？
A: 可以！代码会自动添加英文关键词（如 "landmark travel"），提升匹配度。

### Q4: 达到限额了怎么办？
- **Unsplash**：50次/小时后暂停，1小时后自动恢复
- **Pexels**：200次/小时，通常足够使用
- **双 API 策略**：互为备份，实际限额更高

### Q5: 如何申请提升 Unsplash 限额？
1. 在应用详情页点击 **Request rate limit increase**
2. 说明用途（如：AI travel planning for production use）
3. 提供应用URL（如果已部署）
4. 通常1-3天内审批通过，提升到 5000/小时

### Q6: 需要在前端显示 attribution 吗？
- **Unsplash**：必需（API 要求）
- **Pexels**：推荐但非必需
- 项目已自动处理，无需额外配置

### Q7: 图片URL会过期吗？
不会！Unsplash 和 Pexels 的图片URL是永久有效的。

---

## 📝 总结

### ✅ 推荐配置（最佳体验）
```env
UNSPLASH_ACCESS_KEY=你的key  # 高质量首选
PEXELS_API_KEY=你的key       # 完美备份
```

### ⏱️ 预计耗时
- Unsplash 注册：3-5分钟
- Pexels 注册：2-3分钟
- **总计**：10分钟内完成两个配置

### 🎯 配置后效果
- 🖼️ 每个景点显示3张真实照片
- 🌍 覆盖全球99%热门目的地
- ⚡ 图片加载速度快
- 📱 适配移动端和桌面端

---

## 🔗 相关链接

- **Unsplash 开发者文档**：https://unsplash.com/documentation
- **Pexels API 文档**：https://www.pexels.com/api/documentation/
- **项目图片服务代码**：`backend/app/image_search.py`

---

需要帮助？查看 [README.md](README.md) 或提交 Issue！

最后更新：2026年1月7日
