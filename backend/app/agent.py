"""
TravelPlanGPT Agent - Core Planning Logic
"""
import os
import json
import logging
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel as PydanticBaseModel
from app.models import (
    TravelRequest, TravelItinerary, DailyPlan, Activity,
    HiddenGem, PracticalTips, BudgetOverview, BudgetItem
)
from app.tools import (
    search_attractions,
    search_restaurants,
    get_place_images,
    get_weather_info
)
from app.image_search import get_image_for_activity
from app.database import settings

logger = logging.getLogger(__name__)


class TravelPlanningAgent:
    """AI旅行规划Agent"""
    
    def __init__(self):
        # 优先使用新配置方式，如果未设置则使用旧方式（兼容）
        provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else ""
        
        # 检查是否使用旧配置方式
        if settings.LLM_API_KEY and settings.LLM_OPENAI_BASE:
            # 使用旧配置方式（兼容原有配置）
            api_key = settings.LLM_API_KEY
            base_url = settings.LLM_OPENAI_BASE
            model_name = settings.LLM_MODEL_NAME or "qwen3:8b"
            logger.info(f"使用旧配置方式，模型: {model_name}, URL: {base_url}")
        elif provider == "nvidia":
            # NVIDIA GLM API
            if not settings.NVIDIA_API_KEY or settings.NVIDIA_API_KEY == "":
                raise ValueError("NVIDIA_API_KEY未配置，请在.env文件中设置")
            api_key = settings.NVIDIA_API_KEY
            base_url = "https://integrate.api.nvidia.com/v1"
            model_name = settings.NVIDIA_MODEL
            logger.info(f"使用NVIDIA GLM API，模型: {model_name}")
        elif provider == "ollama" or (not provider and not settings.LLM_API_KEY):
            # 本地Ollama（默认）
            api_key = "ollama"  # Ollama不需要真正的key
            base_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1"
            model_name = settings.OLLAMA_MODEL
            logger.info(f"使用本地Ollama，模型: {model_name}, URL: {base_url}")
        elif provider == "dashscope":
            # 阿里云DashScope (OpenAI兼容接口)
            if not settings.DASHSCOPE_API_KEY or settings.DASHSCOPE_API_KEY == "":
                raise ValueError("DASHSCOPE_API_KEY未配置，请在.env文件中设置")
            api_key = settings.DASHSCOPE_API_KEY
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            model_name = "qwen-plus"
            logger.info(f"使用阿里云DashScope，模型: {model_name}")
        else:
            # 默认使用Ollama
            api_key = "ollama"
            base_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1"
            model_name = settings.OLLAMA_MODEL
            logger.info(f"使用默认配置（本地Ollama），模型: {model_name}, URL: {base_url}")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=api_key,
            base_url=base_url
        )
        
        # 初始化工具
        self.tools = self._init_tools()
        
        # 创建prompt模板
        self.prompt = self._create_prompt_template()
        
        # 创建agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10
        )
    
    def _init_tools(self) -> List[Tool]:
        """初始化Agent工具"""
        tools = []
        
        # Tavily搜索工具（用于搜索景点、餐厅等）
        if os.getenv("TAVILY_API_KEY"):
            tavily_tool = TavilySearchResults(
                max_results=5,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False
            )
            tools.append(tavily_tool)
        
        # 自定义工具
        tools.extend([
            Tool(
                name="SearchAttractions",
                func=search_attractions,
                description="搜索目的地的热门景点和小众景点。输入：城市名称。返回：景点列表及详细信息。"
            ),
            Tool(
                name="SearchRestaurants",
                func=search_restaurants,
                description="搜索目的地的餐厅和美食。输入：城市名称和美食类型。返回：餐厅推荐列表。"
            ),
            Tool(
                name="GetPlaceImages",
                func=get_place_images,
                description="获取景点或餐厅的图片URL。输入：地点名称。返回：图片URL列表。"
            ),
            Tool(
                name="GetWeatherInfo",
                func=get_weather_info,
                description="获取目的地的天气信息。输入：城市名称。返回：天气预报和建议。"
            )
        ])
        
        return tools
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """创建Agent的prompt模板"""
        # 使用自定义的 parser 而不是 langchain 的 parser，避免 pydantic 版本冲突
        # parser = JsonOutputParser(pydantic_object=TravelItinerary)
        # format_instructions = parser.get_format_instructions()
        format_instructions = "The output should be formatted as a JSON instance that conforms to the JSON schema below.\n\n" + \
                             json.dumps(TravelItinerary.model_json_schema(), indent=2)

        system_message = """你是一个专业的旅行规划AI助手 TravelPlanGPT。你的任务是根据用户需求，生成详细、个性化的周末旅行行程。

你需要：
1. 深入分析用户的偏好和预算
2. 使用工具搜索目的地的景点、餐厅、天气等信息
3. 规划合理的每日行程，包括时间、地点、费用
4. 推荐2-3个"隐藏宝石"（本地人才知道的小众地点）
5. 提供实用的旅行建议（交通、天气、打包清单等）

【重要规则】地址信息要求：
- 必须提供真实、具体的地址，包含区名和街道名称
- 禁止使用模糊地址，如"市中心XX路123号"、"美食街"、"某创意园区"
- 餐厅地址示例：上海市黄浦区豫园路85号（南翔馒头店）
- 景点地址示例：北京市东城区景山前街4号（故宫博物院）
- 如果不确定具体地址，使用知名地标或区域，如"黄浦区外滩沿线"、"成都市锦里古街内"

【🚨 严禁生成图片URL - 系统自动处理 🚨】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 图片处理方式：
   - 系统后端会通过 Unsplash 和 Pexels API 自动获取真实照片
   - 你只需要提供准确的活动名称（如"故宫博物院"、"南翔馒头店"）
   
🚫 绝对禁止：
   - 不要在 activities 中添加 "images" 字段
   - 不要生成任何图片URL，包括：
     * picsum.photos（占位图）
     * placeholder.com（占位图）
     * placehold.co（占位图）
     * 任何 unsplash.com 链接
     * 任何 pexels.com 链接
     * 任何其他图片链接
   - JSON 输出中不应包含任何 "images" 键

📋 正确的 Activity JSON 格式（无 images 字段）：
   {
     "time": "09:00",
     "title": "故宫博物院",
     "description": "门票60元。世界最大的古代宫殿建筑群...",
     "duration": "3小时",
     "cost": 60.0,
     "address": "东城区景山前街4号",
     "reason": "必游景点，感受皇家文化"
   }
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

其他注意事项：
- 行程要符合实际，时间安排合理（考虑交通时间）
- 预算分配要详细（交通、住宿、餐饮、景点、杂费）
- 景点推荐要平衡热门和小众
- 描述要生动、有吸引力
- 必须包含"为什么推荐"的理由

请根据用户输入，调用相关工具获取信息，然后生成完整的行程计划。

重要：最终输出必须是符合以下格式的严格JSON：
{format_instructions}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]).partial(format_instructions=format_instructions)
        
        return prompt
    
    async def generate_itinerary(self, request: TravelRequest) -> TravelItinerary:
        """生成旅行行程"""
        
        # 构建输入
        user_input = f"""
请为我规划一个{request.destination}的{request.days}天旅行行程。

详细需求：
- 目的地：{request.destination}
- 天数：{request.days}天
- 预算：{request.budget}
- 出行人数：{request.travelers}人
- 偏好：{', '.join(request.preferences) if request.preferences else '无特殊偏好'}
- 额外要求：{request.extraRequirements if request.extraRequirements else '无'}

请生成包含以下内容的完整行程：
1. 预算总览（总预算和分类明细）
2. 每日详细行程（时间、地点、活动、费用、推荐理由）
3. 隐藏宝石推荐（2-3个本地人才知道的小众地点）
4. 实用旅行建议（交通、天气、打包清单、季节注意事项）

请确保行程实用、有趣、符合预算。
"""
        
        try:
            # 直接使用 LLM 生成，不使用 agent executor（避免工具调用问题）
            print(f"Generating itinerary for {request.destination} using LLM directly...")
            
            # 使用更详细的 prompt
            detailed_prompt = f"""你是专业的旅行规划助手。请为 {request.destination} 生成 {request.days} 天的详细旅行计划。

【重要】请使用简体中文输出所有内容，不要使用繁体中文。

用户需求：
- 目的地：{request.destination}
- 天数：{request.days}天
- 预算：{request.budget}
- 人数：{request.travelers}人
- 偏好：{', '.join(request.preferences) if request.preferences else '无'}
- 额外要求：{request.extraRequirements if request.extraRequirements else '无'}

【关键要求】：
1. 地址格式：必须包含"区+街道+门牌号"或"区+路名+标志性地点"
   ✓ 正确示例：南山区科苑路15号科兴科学园
   ✗ 错误示例：市中心、美食街、某某路

2. 活动名称要求：使用具体明确的名称
   - ✓ 正确："故宫博物院"、"南翔馒头店"、"外滩"
   - ✗ 错误："参观景点"、"午餐"、"购物"

3. 【🚨🚨🚨 严禁生成图片 - 后端通过 Unsplash/Pexels API 自动添加 🚨🚨🚨】
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   
   ⚠️  重要：图片由后端系统自动处理，您无需提供！
   
   🚫 绝对禁止在 JSON 输出中包含 "images" 字段：
      ❌ 不要写 "images": ["https://picsum.photos/..."]
      ❌ 不要写 "images": ["https://images.unsplash.com/..."]
      ❌ 不要写 "images": []
      ❌ 不要在 activity 对象中添加任何 images 相关的键
   
   ✅ 正确做法：
      1. 提供准确的活动名称（如 "故宫博物院" 而不是 "参观景点"）
      2. 后端会调用 Unsplash API 和 Pexels API 获取真实照片
      3. 系统会自动为每个活动匹配 3 张专业旅行摄影作品
   
   📋 正确的 Activity JSON 示例（注意：没有 images 字段）：
      {{
        "time": "09:00",
        "title": "外滩",
        "description": "免费活动。外滩是上海最具代表性的...",
        "duration": "1.5小时",
        "cost": 0.0,
        "address": "黄浦区中山东一路",
        "reason": "上海地标，必游景点"
      }}
   
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. 真实性：推荐真实存在的知名景点和餐厅
   - 使用你所知道的{request.destination}的著名景点
   - 包括门票价格、营业时间等真实信息

4. 价格说明（非常重要 - 适用于所有活动）：
   
   【所有活动的 description 都必须以价格说明开头】：
   
   餐饮活动：
   ✓ "人均约120元。这家餐厅提供正宗川菜..."
   ✓ "人均80-150元。推荐招牌烤鸭..."
   
   景点门票：
   ✓ "门票50元。这是城市最著名的..."
   ✓ "免费参观。博物馆展示了..."
   ✓ "门票30-50元（学生票30元）。..."
   
   交通费用：
   ✓ "打车约20元。从酒店到..."
   ✓ "地铁5元。乘坐2号线..."
   
   住宿（如有）：
   ✓ "每晚约300-500元。精品酒店..."
   
   购物/其他：
   ✓ "预算约100-200元。适合购买..."
   ✓ "约50元。租借自行车..."
   
   免费活动：
   ✓ "免费活动。在公园散步..."
   
   总结：无论什么类型的活动，description 开头必须说明费用！

5. 预算分配要合理：
   - 住宿占30-40%
   - 餐饮占25-35%
   - 交通占10-15%
   - 景点门票占10-20%
   - 其他占10%

请以 JSON 格式输出，严格遵循以下结构（注意：activities 中不要包含 images 字段）：
{{
  "overview": {{
    "totalBudget": {self._estimate_budget(request.budget, request.days, request.travelers)},
    "budgetBreakdown": [
      {{"category": "住宿", "amount": 1200.0}},
      {{"category": "餐饮", "amount": 1000.0}},
      {{"category": "交通", "amount": 400.0}},
      {{"category": "景点门票", "amount": 300.0}},
      {{"category": "购物与杂费", "amount": 600.0}}
    ]
  }},
  "dailyPlans": [
    {{
      "day": 1,
      "title": "Day 1: 标题描述",
      "activities": [
        {{
          "time": "09:00",
          "title": "景点名称（必须具体，如'故宫博物院'）",
          "description": "门票50元。详细描述景点特色和看点...",
          "duration": "2小时",
          "cost": 50.0,
          "address": "区名+街道+门牌号（必须具体）",
          "reason": "推荐理由（50字左右）"
          // 注意：不要添加 "images" 字段！系统会自动通过 Unsplash/Pexels API 添加真实照片
        }},
        {{
          "time": "12:00",
          "title": "午餐：南翔馒头店（必须是具体餐厅名）",
          "description": "人均约120元。品尝地道美食，推荐招牌菜小笼包...",
          "duration": "1.5小时",
          "cost": 120.0,
          "address": "具体餐厅地址",
          "reason": "推荐理由"
          // 注意：不要添加 "images" 字段！
        }},
        {{
          "time": "14:30",
          "title": "文化体验：上海博物馆",
          "description": "免费参观。深入了解当地文化...",
          "duration": "2小时",
          "cost": 0.0,
          "address": "具体地址",
          "reason": "推荐理由"
          // 注意：不要添加 "images" 字段！
        }}
      ]
    }}
  ],
  "hiddenGems": [
    {{
      "title": "小众地点名称",
      "description": "描述（包含位置信息）",
      "category": "分类"
    }},
    {{
      "title": "另一个隐藏宝石",
      "description": "描述（包含位置信息）",
      "category": "分类"
    }},
    {{
      "title": "第三个推荐",
      "description": "描述（包含位置信息）",
      "category": "分类"
    }}
  ],
  "practicalTips": {{
    "transportation": "交通建议（推荐公交/地铁线路）",
    "packingList": ["舒适步行鞋", "防晒霜", "雨伞", "充电宝", "相机"],
    "weather": "天气提示和穿衣建议",
    "seasonalNotes": "季节注意事项"
  }}
}}

重要：只输出 JSON 数据，不要添加任何其他说明文字。确保 JSON 格式完全正确，可以被直接解析。
请务必使用简体中文，不要使用繁体中文（如：台湾→台湾、餐厅→餐厅、景点→景点）。"""

            print("\n🤖 调用 LLM...")
            response = await self.llm.ainvoke(detailed_prompt)
            output = response.content if hasattr(response, 'content') else str(response)
            
            print(f"✅ LLM response received, length: {len(output)}")
            print(f"📝 Response preview (first 200 chars): {output[:200]}...")
            
            # 解析结果
            print("\n📋 开始解析 LLM 输出...")
            itinerary = self._parse_agent_output(output, request)
            print("✅ 解析完成，准备返回行程")
            return itinerary
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in generate_itinerary: {e}")
            # 直接抛出异常，不使用 mock 数据
            raise Exception(f"Failed to generate itinerary: {str(e)}")
    
    def _parse_agent_output(self, output: str, request: TravelRequest) -> TravelItinerary:
        """解析Agent输出为结构化数据"""
        print("\n" + "="*70)
        print("📋 _parse_agent_output 被调用")
        print("="*70)
        try:
            # 尝试查找JSON字符串（处理可能的Markdown代码块）
            text = output.strip()
            print(f"1️⃣ 原始输出长度: {len(text)}")
            
            # 移除可能的 markdown 代码块标记
            if "```json" in text:
                print("2️⃣ 检测到 ```json 标记，正在移除...")
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                print("2️⃣ 检测到 ``` 标记，正在移除...")
                text = text.split("```")[1].split("```")[0].strip()
            else:
                print("2️⃣ 未检测到代码块标记")
            
            # 查找第一个 { 和最后一个 }
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                print(f"3️⃣ 提取 JSON: 从位置 {start_idx} 到 {end_idx}")
                text = text[start_idx:end_idx+1]
            
            # 尝试解析 JSON
            print(f"4️⃣ 尝试解析 JSON, 长度: {len(text)}")
            data = json.loads(text)
            print(f"✅ JSON 解析成功！")
            
            # 验证必要字段
            if 'overview' not in data or 'dailyPlans' not in data:
                print(f"❌ 缺少必需字段: overview={('overview' in data)}, dailyPlans={('dailyPlans' in data)}")
                raise ValueError("Missing required fields")
            
            print(f"5️⃣ 验证字段通过")
            
            # 构建 TravelItinerary 对象
            print(f"6️⃣ 构建 TravelItinerary 对象...")
            itinerary = TravelItinerary(**data)
            print(f"✅ TravelItinerary 创建成功: {len(itinerary.dailyPlans)} 天行程")
            
            # 🔍 调试：检查LLM是否生成了images字段
            print(f"\n🔍 调试：检查LLM生成的数据中是否包含images字段...")
            llm_has_images = False
            for day in itinerary.dailyPlans:
                for activity in day.activities:
                    if hasattr(activity, 'images') and activity.images:
                        llm_has_images = True
                        print(f"⚠️  警告：LLM为 '{activity.title}' 生成了 {len(activity.images)} 个images:")
                        for img in activity.images[:2]:
                            print(f"     - {img[:80]}...")
            
            if not llm_has_images:
                print(f"✅ LLM未生成images字段（符合预期）")
            else:
                print(f"❌ LLM生成了images字段（违反了Prompt指示）")
            
            # 为每个活动添加真实图片
            print(f"\n7️⃣ 准备调用 _add_images_to_itinerary()...")
            itinerary = self._add_images_to_itinerary(itinerary, request.destination)
            print(f"✅ 图片添加完成")
            
            return itinerary
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Problematic text (first 500 chars): {output[:500]}")
            raise Exception(f"Failed to parse LLM output as JSON: {e}")
        except Exception as e:
            print(f"Error creating TravelItinerary: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to create TravelItinerary: {e}")
    

    
    def _add_images_to_itinerary(self, itinerary: TravelItinerary, destination: str) -> TravelItinerary:
        """为行程中的每个活动添加真实图片（纯同步方式，带全局去重）"""
        import logging
        logger = logging.getLogger(__name__)
        
        print("\n" + "="*60)
        print("🖼️  _add_images_to_itinerary 被调用!")
        print(f"   目的地: {destination}")
        print("="*60)
        
        logger.info("\n" + "="*60)
        logger.info("🖼️  开始为活动添加真实图片...")
        logger.info("="*60)
        
        # 全局已使用图片集合（用于去重）
        used_images: set = set()
        
        # 🔧 第一步：强制清除所有LLM可能生成的图片
        print("🧹 第一步：清除所有现有图片...")
        logger.info("🧹 第一步：清除所有现有图片...")
        cleaned_count = 0
        for daily_plan in itinerary.dailyPlans:
            for activity in daily_plan.activities:
                if hasattr(activity, 'images') and activity.images:
                    old_images = activity.images.copy()
                    activity.images = []
                    cleaned_count += 1
                    print(f"   ⚠️  清除了 '{activity.title}' 的 {len(old_images)} 张图片")
                    logger.warning(f"   ⚠️  清除了 '{activity.title}' 的 {len(old_images)} 张图片:")
                    for img in old_images[:1]:
                        if 'picsum' in img or 'placeholder' in img or 'placehold' in img:
                            print(f"      ❌ 占位图: {img[:60]}...")
                            logger.warning(f"      ❌ 占位图: {img[:60]}...")
                        else:
                            print(f"      🗑️  其他: {img[:60]}...")
                            logger.info(f"      🗑️  其他: {img[:60]}...")
        
        if cleaned_count > 0:
            print(f"✅ 已清除 {cleaned_count} 个活动的原有图片")
            logger.info(f"✅ 已清除 {cleaned_count} 个活动的原有图片")
        else:
            print(f"✅ 无需清除（LLM未生成图片）")
            logger.info(f"✅ 无需清除（LLM未生成图片）")
        
        # 🔧 第二步：同步获取图片（带全局去重）
        print("\n📸 第二步：从 API 获取真实图片...")
        
        for daily_plan in itinerary.dailyPlans:
            print(f"\n📅 Day {daily_plan.day}: {daily_plan.title}")
            logger.info(f"\n📅 Day {daily_plan.day}: {daily_plan.title}")
            print("-" * 60)
            logger.info("-" * 60)
            
            for idx, activity in enumerate(daily_plan.activities, 1):
                print(f"\n🎯 处理活动 {idx}: {activity.title}")
                logger.info(f"\n🎯 处理活动 {idx}: {activity.title}")
                
                # 确定活动类型
                category = ""
                if "餐" in activity.title or "吃" in activity.title or "美食" in activity.title:
                    category = "美食"
                elif "博物" in activity.title or "寺" in activity.title or "庙" in activity.title:
                    category = "博物馆"
                elif "公园" in activity.title or "花园" in activity.title:
                    category = "公园"
                elif "购物" in activity.title or "商场" in activity.title:
                    category = "购物"
                else:
                    category = "景点"
                
                print(f"   📂 分类: {category}")
                logger.debug(f"   📂 分类: {category}")
                
                # 获取图片（不使用占位图）
                try:
                    images = get_image_for_activity(
                        activity_name=activity.title,
                        location=destination,
                        category=category
                    )
                    
                    # 全局去重：过滤掉已经在其他活动中使用过的图片
                    if images:
                        unique_images = []
                        for img in images:
                            # 提取图片ID（Pexels格式：包含数字ID）
                            img_id = self._extract_image_id(img)
                            if img_id not in used_images:
                                unique_images.append(img)
                                used_images.add(img_id)
                            else:
                                print(f"   🔄 跳过重复图片: ...{img[-50:]}")
                                logger.info(f"   🔄 跳过重复图片: ...{img[-50:]}")
                        
                        images = unique_images
                    
                    activity.images = images if images else []
                    
                    if images:
                        print(f"   ✅ 成功添加 {len(images)} 张唯一图片")
                        logger.info(f"   ✅ 成功添加 {len(images)} 张唯一图片")
                        for i, img in enumerate(images[:2], 1):
                            print(f"      {i}. {img[:70]}...")
                    else:
                        print(f"   ⚠️  未找到唯一图片（将不显示图片）")
                        logger.warning(f"   ⚠️  未找到唯一图片（将不显示图片）")
                        
                except Exception as e:
                    print(f"   ❌ 获取图片失败: {e}")
                    logger.error(f"   ❌ 获取图片失败: {e}")
                    import traceback
                    traceback.print_exc()
                    activity.images = []
        
        print("\n" + "="*60)
        print("✅ 图片添加完成！")
        print(f"   共使用 {len(used_images)} 张唯一图片")
        print("="*60 + "\n")
        logger.info("\n" + "="*60)
        logger.info("✅ 图片添加完成！")
        logger.info(f"   共使用 {len(used_images)} 张唯一图片")
        logger.info("="*60 + "\n")
        
        return itinerary
    
    def _extract_image_id(self, url: str) -> str:
        """从图片URL中提取唯一标识符，用于去重"""
        import re
        
        # Pexels URL 格式: https://images.pexels.com/photos/12345678/pexels-photo-12345678.jpeg
        pexels_match = re.search(r'/photos/(\d+)/', url)
        if pexels_match:
            return f"pexels_{pexels_match.group(1)}"
        
        # Unsplash URL 格式: https://images.unsplash.com/photo-1234567890-abcdef...
        unsplash_match = re.search(r'/photo-([a-zA-Z0-9-]+)', url)
        if unsplash_match:
            return f"unsplash_{unsplash_match.group(1)}"
        
        # 其他情况：使用完整URL作为ID
        return url
    
    def _estimate_budget(self, budget_str: str, days: int, travelers: int) -> float:
        """从预算字符串估算总预算"""
        if not budget_str:
            return 2000.0 * days * travelers
        
        # 简单解析，如"2000-5000元"
        import re
        numbers = re.findall(r'\d+', budget_str)
        if numbers:
            # 取中间值
            avg = sum(map(float, numbers)) / len(numbers)
            return avg
        return 2000.0 * days
    

