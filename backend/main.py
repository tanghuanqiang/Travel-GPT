from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from app.agent import TravelPlanningAgent
from app.models import TravelRequest, TravelItinerary
from app.database import get_db, engine, Base
from app.db_models import User, Itinerary
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user,
    get_current_user_optional
)

# Load environment variables
load_dotenv()

# 确保数据库表已创建
Base.metadata.create_all(bind=engine)

logger.info("="*70)
logger.info("🚀 Travel-GPT Backend 正在初始化...")
logger.info("="*70)

app = FastAPI(
    title="TravelPlanGPT API",
    description="AI-powered weekend travel planning API",
    version="1.0.0"
)


# ============ Pydantic Models for Auth ============
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: str

class ItineraryResponse(BaseModel):
    id: int
    destination: str
    days: int
    created_at: str
    itinerary_data: dict

# CORS middleware - 必须在定义路由之前添加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error: {exc.errors()}")
    print(f"Body: {excel.body if hasattr(exc, 'body') else 'N/A'}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )

# Initialize agent
travel_agent = TravelPlanningAgent()


@app.get("/")
async def root():
    return {
        "message": "Welcome to TravelPlanGPT API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/test-cors")
async def test_cors():
    """测试 CORS 配置"""
    return {"message": "CORS is working!", "timestamp": "2026-01-06"}


# ============ Auth Endpoints ============
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="该邮箱已被注册")
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 生成 token (转换 ID 为字符串)
        access_token = create_access_token(data={"sub": str(new_user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "created_at": str(new_user.created_at)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    try:
        # 查找用户
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="邮箱或密码错误")
        
        # 生成 token (转换 ID 为字符串)
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "created_at": str(user.created_at)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": str(current_user.created_at)
    }


@app.get("/api/test")
async def test_endpoint():
    """测试端点 - 验证后端是否正常工作"""
    logger.info("\n" + "🧪"*30)
    logger.info("✅ 测试端点被调用！")
    logger.info("🧪"*30 + "\n")
    return {"status": "ok", "message": "后端正常工作！", "logging": "使用 logger"}


@app.post("/api/generate-plan", response_model=TravelItinerary)
async def generate_travel_plan(
    request: TravelRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Generate a travel itinerary based on user requirements
    支持登录和未登录用户，登录用户会保存历史记录
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 [API] 收到生成行程请求")
    logger.info("="*80)
    logger.info(f"📍 目的地: {request.destination}")
    logger.info(f"📅 天数: {request.days}")
    logger.info(f"💰 预算: {request.budget}")
    logger.info(f"👥 人数: {request.travelers}")
    logger.info(f"🎯 偏好: {request.preferences}")
    logger.info(f"👤 用户: {'已登录' if current_user else '未登录'}")
    logger.info("="*80 + "\n")
    
    try:
        # 每次都重新生成行程（不使用缓存）
        logger.info("🤖 开始调用 travel_agent.generate_itinerary()...")
        itinerary = await travel_agent.generate_itinerary(request)
        logger.info("✅ 行程生成完成！")
        
        # 如果用户已登录，保存到数据库
        if current_user:
            itinerary_record = Itinerary(
                user_id=current_user.id,
                agent_name=request.agentName,
                destination=request.destination,
                days=request.days,
                budget=request.budget,
                travelers=request.travelers,
                preferences=json.dumps(request.preferences, ensure_ascii=False),
                extra_requirements=request.extraRequirements,
                itinerary_data=itinerary.model_dump_json(),
                total_budget=itinerary.overview.totalBudget if itinerary.overview else None
            )
            db.add(itinerary_record)
            db.commit()
            print(f"[INFO] 已保存行程: 用户 {current_user.id}, 目的地 {request.destination}")
        
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


# ============ History Endpoints ============
@app.get("/api/history")
async def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """获取用户的历史行程记录"""
    try:
        itineraries = db.query(Itinerary)\
            .filter(Itinerary.user_id == current_user.id)\
            .order_by(Itinerary.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        total = db.query(Itinerary).filter(Itinerary.user_id == current_user.id).count()
        
        return {
            "total": total,
            "items": [
                {
                    "id": item.id,
                    "destination": item.destination,
                    "days": item.days,
                    "budget": item.budget,
                    "created_at": str(item.created_at),
                    "preview": {
                        "agentName": item.agent_name,
                        "travelers": item.travelers,
                        "totalBudget": item.total_budget
                    }
                }
                for item in itineraries
            ]
        }
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@app.get("/api/history/{itinerary_id}")
async def get_itinerary_detail(
    itinerary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个行程的详细信息"""
    try:
        itinerary = db.query(Itinerary)\
            .filter(Itinerary.id == itinerary_id, Itinerary.user_id == current_user.id)\
            .first()
        
        if not itinerary:
            raise HTTPException(status_code=404, detail="行程不存在或无权访问")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching itinerary: {e}")
        raise HTTPException(status_code=500, detail=f"获取行程失败: {str(e)}")
    
    return {
        "id": itinerary.id,
        "destination": itinerary.destination,
        "days": itinerary.days,
        "created_at": str(itinerary.created_at),
        "itinerary": json.loads(itinerary.itinerary_data)
    }


@app.delete("/api/history/{itinerary_id}")
async def delete_itinerary(
    itinerary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除历史行程"""
    itinerary = db.query(Itinerary)\
        .filter(Itinerary.id == itinerary_id, Itinerary.user_id == current_user.id)\
        .first()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="行程不存在")
    
    db.delete(itinerary)
    db.commit()
    
    return {"message": "删除成功"}


if __name__ == "__main__":
    import sys
    # 强制刷新 stdout，确保 print 立即输出
    sys.stdout.reconfigure(line_buffering=True)
    
    print("\n" + "="*70)
    print("🚀 Travel-GPT Backend Server Starting...")
    print("="*70)
    print("📍 Host: 0.0.0.0")
    print("🔌 Port: 8000")
    print("🔄 Hot Reload: Enabled")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
