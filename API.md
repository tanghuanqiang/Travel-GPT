# TravelPlanGPT API 使用文档

## API Endpoints

### 1. 生成旅行计划

**Endpoint**: `POST /api/generate-plan`

**请求体**:
```json
{
  "agentName": "我的周末旅行",
  "destination": "上海",
  "days": 2,
  "budget": "2000-5000元",
  "travelers": 2,
  "preferences": ["美食", "文化"],
  "extraRequirements": "避免热门景点"
}
```

**响应**:
```json
{
  "overview": {
    "totalBudget": 3000,
    "budgetBreakdown": [
      {"category": "交通", "amount": 500},
      {"category": "住宿", "amount": 800},
      {"category": "餐饮", "amount": 1000},
      {"category": "景点", "amount": 500},
      {"category": "杂费", "amount": 200}
    ]
  },
  "dailyPlans": [
    {
      "day": 1,
      "title": "抵达与探索",
      "activities": [
        {
          "time": "09:00",
          "title": "外滩晨景",
          "description": "...",
          "duration": "2小时",
          "cost": 0,
          "address": "...",
          "reason": "...",
          "images": ["url1", "url2"]
        }
      ]
    }
  ],
  "hiddenGems": [
    {
      "title": "本地咖啡馆",
      "description": "...",
      "category": "咖啡"
    }
  ],
  "practicalTips": {
    "transportation": "...",
    "packingList": ["item1", "item2"],
    "weather": "...",
    "seasonalNotes": "..."
  }
}
```

### 2. 健康检查

**Endpoint**: `GET /api/health`

**响应**:
```json
{
  "status": "healthy"
}
```

## 数据模型

### TravelRequest
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agentName | string | 否 | 行程名称 |
| destination | string | 是 | 目的地城市 |
| days | integer | 否 | 旅行天数 (1-5) |
| budget | string | 否 | 预算范围 |
| travelers | integer | 否 | 出行人数 |
| preferences | array | 否 | 偏好标签 |
| extraRequirements | string | 否 | 额外要求 |

### 偏好标签选项
- `food` - 美食
- `outdoor` - 户外
- `shopping` - 购物
- `culture` - 文化
- `relax` - 放松
- `adventure` - 冒险
- `family` - 亲子

## 错误处理

**错误响应格式**:
```json
{
  "detail": "Error message"
}
```

**常见错误码**:
- `400` - 请求参数错误
- `500` - 服务器内部错误（通常是API Key配置问题）

## 使用示例

### cURL
```bash
curl -X POST http://localhost:8000/api/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "上海",
    "days": 2,
    "budget": "3000元",
    "preferences": ["美食", "文化"]
  }'
```

### JavaScript (Axios)
```javascript
import axios from 'axios';

const response = await axios.post('http://localhost:8000/api/generate-plan', {
  destination: '上海',
  days: 2,
  budget: '3000元',
  preferences: ['美食', '文化']
});

console.log(response.data);
```

### Python (Requests)
```python
import requests

response = requests.post(
    'http://localhost:8000/api/generate-plan',
    json={
        'destination': '上海',
        'days': 2,
        'budget': '3000元',
        'preferences': ['美食', '文化']
    }
)

print(response.json())
```
