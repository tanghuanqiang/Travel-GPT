from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
import json
import logging
import secrets
import asyncio
import uuid
import re
from datetime import datetime, timedelta
from urllib.parse import quote

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def safe_filename_for_header(filename: str) -> tuple[str, str]:
    """
    生成安全的HTTP响应头文件名
    返回: (ascii_filename, utf8_encoded_filename)
    """
    # 创建ASCII fallback文件名（移除非ASCII字符）
    ascii_filename = re.sub(r'[^\x00-\x7F]+', '_', filename)
    # 如果原文件名完全是ASCII，直接使用
    if ascii_filename == filename:
        return filename, quote(filename.encode('utf-8'))
    # 否则使用ASCII版本作为fallback，UTF-8版本作为主要
    utf8_encoded = quote(filename.encode('utf-8'))
    return ascii_filename, utf8_encoded


from app.agent import TravelPlanningAgent
from app.models import TravelRequest, TravelItinerary
from app.database import get_db, engine, Base, settings, SessionLocal
from app.db_models import User, Itinerary, EmailVerification, ShareLink, Favorite, TemporaryShare, Task
from app.pdf_export import generate_pdf
from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user,
    get_current_user_optional,
    get_user_by_email,
    create_verification_code,
    verify_verification_code,
    create_reset_password_code,
    update_user_password
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

class VerificationRequest(BaseModel):
    email: str

class VerificationCodeVerify(BaseModel):
    email: str
    code: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class CreateShareLinkRequest(BaseModel):
    is_public: bool = True
    expires_days: Optional[int] = None  # None表示永久有效

class CreateTemporaryShareRequest(BaseModel):
    itinerary_data: dict  # 完整的行程数据
    expires_days: int = 7  # 临时分享默认7天过期

class ExportPDFRequest(BaseModel):
    itinerary_data: dict
    destination: str
    days: int

class UpdateItineraryRequest(BaseModel):
    agent_name: Optional[str] = None
    destination: Optional[str] = None
    days: Optional[int] = None
    budget: Optional[str] = None
    travelers: Optional[int] = None
    preferences: Optional[List[str]] = None
    extra_requirements: Optional[str] = None

class ItineraryResponse(BaseModel):
    id: int
    destination: str
    days: int
    created_at: str
    itinerary_data: dict

# CORS middleware - 必须在定义路由之前添加
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    logger.warning(f"Body: {exc.body if hasattr(exc, 'body') else 'N/A'}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )

# Initialize agent
travel_agent = TravelPlanningAgent()

# 后台任务处理函数
async def process_travel_plan_task(task_id: str, request_data: dict, user_id: Optional[int] = None):
    """
    后台异步处理旅行计划生成任务
    """
    db = SessionLocal()
    try:
        # 更新任务状态为processing
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            logger.error(f"任务 {task_id} 不存在")
            return
        
        task.status = "processing"
        task.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"🤖 [后台任务] 开始处理任务 {task_id}")
        
        # 解析请求数据
        travel_request = TravelRequest(**request_data)
        
        # 生成行程
        itinerary = await travel_agent.generate_itinerary(travel_request)
        logger.info(f"✅ [后台任务] 任务 {task_id} 完成")
        
        # 如果用户已登录，保存到数据库
        itinerary_id = None
        if user_id:
            itinerary_record = Itinerary(
                user_id=user_id,
                agent_name=travel_request.agentName,
                destination=travel_request.destination,
                days=travel_request.days,
                budget=travel_request.budget,
                travelers=travel_request.travelers,
                preferences=json.dumps(travel_request.preferences, ensure_ascii=False),
                extra_requirements=travel_request.extraRequirements,
                itinerary_data=itinerary.model_dump_json(),
                total_budget=itinerary.overview.totalBudget if itinerary.overview else None
            )
            db.add(itinerary_record)
            db.commit()
            db.refresh(itinerary_record)
            itinerary_id = itinerary_record.id
            logger.info(f"[INFO] 已保存行程: 用户 {user_id}, 目的地 {travel_request.destination}")
        
        # 更新任务状态为completed
        task.status = "completed"
        task.result_data = itinerary.model_dump_json()
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ [后台任务] 任务 {task_id} 已保存结果")
        
    except Exception as e:
        logger.error(f"❌ [后台任务] 任务 {task_id} 处理失败: {str(e)}")
        # 更新任务状态为failed
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


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
@app.post("/api/auth/send-verification-code")
async def send_verification_code(
    request: VerificationRequest,
    db: Session = Depends(get_db)
):
    """发送注册验证码到邮箱"""
    # 检查邮箱是否已注册
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 创建并发送验证码
    try:
        create_verification_code(db, request.email)
        return {"message": "验证码已发送，请查收邮箱"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送验证码失败: {str(e)}"
        )


@app.post("/api/auth/verify-code")
async def verify_code(
    request: VerificationCodeVerify,
    db: Session = Depends(get_db)
):
    """验证邮箱验证码"""
    # 检查邮箱是否已注册
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 验证验证码
    is_valid = verify_verification_code(db, request.email, request.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码无效或已过期"
        )
    
    return {"message": "验证成功"}


@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册（需要先验证邮箱验证码）"""
    try:
        # 检查邮箱是否已存在
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="该邮箱已被注册")
        
        # 验证密码长度（bcrypt 限制72字节）
        if len(user_data.password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=400,
                detail="密码长度不能超过72字节，请使用更短的密码"
            )
        
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


@app.put("/api/auth/me/password")
async def update_password(
    request: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少6位"
        )
    
    # 验证旧密码
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "密码修改成功"}


@app.delete("/api/auth/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """注销账号（删除账号及关联数据）"""
    try:
        # 删除用户（关联的行程会自动删除，因为设置了cascade="all, delete-orphan"）
        db.delete(current_user)
        db.commit()
        return {"message": "账号已成功注销"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注销账号失败: {str(e)}"
        )


@app.post("/api/auth/send-reset-password-code")
async def send_reset_password_code(
    request: VerificationRequest,
    db: Session = Depends(get_db)
):
    """发送重置密码验证码"""
    try:
        create_reset_password_code(db, request.email)
        return {"message": "重置密码验证码已发送，请查收邮箱"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送验证码失败: {str(e)}"
        )


@app.post("/api/auth/verify-reset-password-code")
async def verify_reset_password_code(
    request: VerificationCodeVerify,
    db: Session = Depends(get_db)
):
    """验证重置密码验证码"""
    is_valid = verify_verification_code(db, request.email, request.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码无效或已过期"
        )
    
    return {"message": "验证成功"}


@app.post("/api/auth/reset-password", response_model=TokenResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """重置用户密码"""
    # 验证验证码
    is_valid = verify_verification_code(db, request.email, request.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码无效或已过期"
        )
    
    # 重置密码
    try:
        user = update_user_password(db, request.email, request.new_password)
        # 生成 access token 用于自动登录
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置密码失败: {str(e)}"
        )


@app.get("/api/test")
async def test_endpoint():
    """测试端点 - 验证后端是否正常工作"""
    logger.info("\n" + "🧪"*30)
    logger.info("✅ 测试端点被调用！")
    logger.info("🧪"*30 + "\n")
    return {"status": "ok", "message": "后端正常工作！", "logging": "使用 logger"}


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@app.post("/api/generate-plan", response_model=TaskResponse)
async def generate_travel_plan(
    request: TravelRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    创建旅行计划生成任务（异步）
    立即返回任务ID，前端通过轮询 /api/tasks/{task_id} 获取结果
    支持登录和未登录用户，登录用户会保存历史记录
    """
    logger.info("\n" + "="*80)
    logger.info("🚀 [API] 收到生成行程请求（异步模式）")
    logger.info("="*80)
    logger.info(f"📍 目的地: {request.destination}")
    logger.info(f"📅 天数: {request.days}")
    logger.info(f"💰 预算: {request.budget}")
    logger.info(f"👥 人数: {request.travelers}")
    logger.info(f"🎯 偏好: {request.preferences}")
    logger.info(f"👤 用户: {'已登录' if current_user else '未登录'}")
    logger.info("="*80 + "\n")
    
    try:
        # 生成唯一任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task = Task(
            task_id=task_id,
            user_id=current_user.id if current_user else None,
            status="pending",
            request_data=json.dumps(request.model_dump(), ensure_ascii=False)
        )
        db.add(task)
        db.commit()
        
        logger.info(f"✅ 任务 {task_id} 已创建，开始后台处理")
        
        # 启动后台任务
        request_dict = request.model_dump()
        user_id = current_user.id if current_user else None
        asyncio.create_task(process_travel_plan_task(task_id, request_dict, user_id))
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="任务已创建，正在处理中"
        )
    except Exception as e:
        logger.error(f"❌ 创建任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


# ============ Task Endpoints ============
class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[dict] = None  # 完成后的结果数据
    error_message: Optional[str] = None  # 失败时的错误信息
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None

@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """查询任务状态和结果（支持登录和未登录用户）"""
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 如果用户已登录，验证任务是否属于该用户（增强并发安全）
    if current_user and task.user_id is not None:
        if task.user_id != current_user.id:
            logger.warning(f"用户 {current_user.id} 尝试访问不属于自己的任务 {task_id}（任务属于用户 {task.user_id}）")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此任务"
            )
    
    # 验证返回的task_id与请求的task_id匹配（双重验证）
    if task.task_id != task_id:
        logger.error(f"任务ID不匹配！请求: {task_id}, 数据库: {task.task_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="任务ID验证失败"
        )
    
    result_data = None
    if task.result_data:
        try:
            result_data = json.loads(task.result_data)
        except:
            result_data = None
    
    logger.debug(f"查询任务状态: task_id={task_id}, status={task.status}, user_id={current_user.id if current_user else None}")
    
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=result_data,
        error_message=task.error_message,
        created_at=str(task.created_at),
        updated_at=str(task.updated_at) if task.updated_at else str(task.created_at),
        completed_at=str(task.completed_at) if task.completed_at else None
    )


# ============ History Endpoints ============
@app.get("/api/history")
async def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,  # 搜索关键词（目的地、行程名称）
    sort_by: Optional[str] = "created_at",  # 排序字段：created_at, total_budget, days
    sort_order: Optional[str] = "desc",  # 排序顺序：asc, desc
    min_days: Optional[int] = None,  # 最小天数
    max_days: Optional[int] = None,  # 最大天数
    min_budget: Optional[float] = None,  # 最小预算
    max_budget: Optional[float] = None  # 最大预算
):
    """获取用户的历史行程记录（支持搜索、筛选、排序）"""
    try:
        query = db.query(Itinerary).filter(Itinerary.user_id == current_user.id)
        
        # 搜索功能：按目的地或行程名称搜索
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Itinerary.destination.like(search_pattern)) |
                (Itinerary.agent_name.like(search_pattern))
            )
        
        # 筛选功能：按天数范围
        if min_days is not None:
            query = query.filter(Itinerary.days >= min_days)
        if max_days is not None:
            query = query.filter(Itinerary.days <= max_days)
        
        # 筛选功能：按预算范围
        if min_budget is not None:
            query = query.filter(Itinerary.total_budget >= min_budget)
        if max_budget is not None:
            query = query.filter(Itinerary.total_budget <= max_budget)
        
        # 获取所有符合条件的行程（不分页，用于排序）
        all_itineraries = query.all()
        
        # 获取所有行程ID
        itinerary_ids = [item.id for item in all_itineraries]
        
        # 批量查询收藏状态
        favorites = db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.itinerary_id.in_(itinerary_ids)
        ).all()
        
        # 创建收藏状态映射
        favorited_ids = {fav.itinerary_id for fav in favorites}
        
        # 构建响应，包含收藏状态
        items = []
        for item in all_itineraries:
            is_favorited = item.id in favorited_ids
            # 获取排序字段的值
            sort_value = None
            if sort_by == "created_at":
                sort_value = item.created_at.timestamp() if item.created_at else 0
            elif sort_by == "total_budget":
                sort_value = item.total_budget if item.total_budget else 0
            elif sort_by == "days":
                sort_value = item.days if item.days else 0
            else:
                sort_value = item.created_at.timestamp() if item.created_at else 0
            
            items.append({
                "id": item.id,
                "destination": item.destination,
                "days": item.days,
                "budget": item.budget,
                "created_at": str(item.created_at),
                "is_favorited": is_favorited,
                "_sort_value": sort_value,  # 临时字段用于排序
                "preview": {
                    "agentName": item.agent_name,
                    "travelers": item.travelers,
                    "totalBudget": item.total_budget
                }
            })
        
        # 排序：收藏的优先，然后在每个组内按指定字段排序
        # 排序键：(not is_favorited, sort_value)
        # is_favorited=True时，not is_favorited=False，会排在前面（False < True）
        # 对于sort_value，如果sort_order是desc，需要反转，所以使用负值
        reverse_sort = (sort_order == "desc")
        for item in items:
            sort_value = item["_sort_value"]
            if reverse_sort:
                # 对于降序，使用负值，这样排序时小的（负的大值）会排在前面
                item["_sort_key"] = (not item["is_favorited"], -sort_value)
            else:
                # 对于升序，直接使用原值
                item["_sort_key"] = (not item["is_favorited"], sort_value)
        
        items.sort(key=lambda x: x["_sort_key"])
        
        # 移除临时排序字段
        for item in items:
            del item["_sort_value"]
            del item["_sort_key"]
        
        # 获取总数
        total = len(items)
        
        # 分页
        paginated_items = items[offset:offset + limit]
        
        return {
            "total": total,
            "items": paginated_items
        }
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
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


@app.put("/api/itinerary/{itinerary_id}")
async def update_itinerary(
    itinerary_id: int,
    request: UpdateItineraryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新行程基本信息（仅更新请求参数，不重新生成行程）"""
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    # 更新字段
    if request.agent_name is not None:
        itinerary.agent_name = request.agent_name
    if request.destination is not None:
        itinerary.destination = request.destination
    if request.days is not None:
        itinerary.days = request.days
    if request.budget is not None:
        itinerary.budget = request.budget
    if request.travelers is not None:
        itinerary.travelers = request.travelers
    if request.preferences is not None:
        itinerary.preferences = json.dumps(request.preferences, ensure_ascii=False)
    if request.extra_requirements is not None:
        itinerary.extra_requirements = request.extra_requirements
    
    db.commit()
    db.refresh(itinerary)
    
    return {
        "id": itinerary.id,
        "destination": itinerary.destination,
        "days": itinerary.days,
        "message": "行程信息已更新"
    }


@app.post("/api/itinerary/{itinerary_id}/regenerate")
async def regenerate_itinerary(
    itinerary_id: int,
    request: Optional[TravelRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """重新生成行程（基于现有行程或新的请求参数）"""
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    try:
        # 如果没有提供新的请求参数，使用现有行程的参数
        if request is None:
            request = TravelRequest(
                agentName=itinerary.agent_name or "我的周末旅行",
                destination=itinerary.destination,
                days=itinerary.days,
                budget=itinerary.budget or "",
                travelers=itinerary.travelers or 2,
                preferences=json.loads(itinerary.preferences) if itinerary.preferences else [],
                extraRequirements=itinerary.extra_requirements or ""
            )
        
        # 重新生成行程
        new_itinerary = await travel_agent.generate_itinerary(request)
        
        # 更新数据库中的行程数据
        itinerary.agent_name = request.agentName
        itinerary.destination = request.destination
        itinerary.days = request.days
        itinerary.budget = request.budget
        itinerary.travelers = request.travelers
        itinerary.preferences = json.dumps(request.preferences, ensure_ascii=False)
        itinerary.extra_requirements = request.extraRequirements
        itinerary.itinerary_data = new_itinerary.model_dump_json()
        itinerary.total_budget = new_itinerary.overview.totalBudget if new_itinerary.overview else None
        
        db.commit()
        db.refresh(itinerary)
        
        return new_itinerary
    except Exception as e:
        logger.error(f"重新生成行程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新生成行程失败: {str(e)}"
        )


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


# ============ Export Endpoints ============
@app.get("/api/itinerary/{itinerary_id}/export/pdf")
async def export_itinerary_pdf(
    itinerary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出行程为PDF（需要登录）"""
    # 获取行程
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    try:
        # 解析行程数据
        if isinstance(itinerary.itinerary_data, str):
            itinerary_data = json.loads(itinerary.itinerary_data)
        else:
            itinerary_data = itinerary.itinerary_data
        
        # 生成PDF
        destination = itinerary.destination or "未知目的地"
        days = itinerary.days or 1
        pdf_buffer = generate_pdf(itinerary_data, destination, days)
        
        # 返回PDF文件（处理中文文件名编码）
        filename = f"{destination}_{days}天行程.pdf"
        ascii_filename, utf8_encoded = safe_filename_for_header(filename)
        return Response(
            content=pdf_buffer.read(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{utf8_encoded}'
            }
        )
    except json.JSONDecodeError as e:
        logger.error(f"PDF生成失败 - JSON解析错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: 行程数据格式错误 - {str(e)}"
        )
    except Exception as e:
        logger.error(f"PDF生成失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: {str(e)}"
        )


@app.get("/api/share/{share_token}/export/pdf")
async def export_shared_itinerary_pdf(
    share_token: str,
    db: Session = Depends(get_db)
):
    """导出分享的行程为PDF（无需登录）"""
    # 先尝试查找永久分享
    share_link = db.query(ShareLink).filter(ShareLink.share_token == share_token).first()
    
    if share_link:
        # 获取关联的行程
        itinerary = db.query(Itinerary).filter(Itinerary.id == share_link.itinerary_id).first()
        
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="行程不存在"
            )
        
        # 检查是否过期
        if share_link.expires_at and datetime.utcnow() > share_link.expires_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="分享链接已过期"
            )
        
        if isinstance(itinerary.itinerary_data, str):
            itinerary_data = json.loads(itinerary.itinerary_data)
        else:
            itinerary_data = itinerary.itinerary_data
        destination = itinerary.destination or "未知目的地"
        days = itinerary.days or len(itinerary_data.get("dailyPlans", [])) or 1
    else:
        # 尝试查找临时分享
        temporary_share = db.query(TemporaryShare).filter(TemporaryShare.share_token == share_token).first()
        
        if not temporary_share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分享链接不存在"
            )
        
        # 检查是否过期
        if datetime.utcnow() > temporary_share.expires_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="分享链接已过期"
            )
        
        if isinstance(temporary_share.itinerary_data, str):
            itinerary_data = json.loads(temporary_share.itinerary_data)
        else:
            itinerary_data = temporary_share.itinerary_data
        destination = itinerary_data.get("destination") or "未知目的地"
        days = itinerary_data.get("days") or len(itinerary_data.get("dailyPlans", [])) or 1
    
    try:
        # 生成PDF
        destination = destination or "未知目的地"
        days = days or 1
        pdf_buffer = generate_pdf(itinerary_data, destination, days)
        
        # 返回PDF文件（处理中文文件名编码）
        filename = f"{destination}_{days}天行程.pdf"
        ascii_filename, utf8_encoded = safe_filename_for_header(filename)
        return Response(
            content=pdf_buffer.read(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{utf8_encoded}'
            }
        )
    except json.JSONDecodeError as e:
        logger.error(f"PDF生成失败 - JSON解析错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: 行程数据格式错误 - {str(e)}"
        )
    except Exception as e:
        logger.error(f"PDF生成失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: {str(e)}"
        )


@app.post("/api/export/pdf")
async def export_pdf_from_data(
    request: ExportPDFRequest,
    db: Session = Depends(get_db)
):
    """直接从行程数据导出PDF（无需登录，用于游客用户）"""
    try:
        # 生成PDF
        destination = request.destination or "未知目的地"
        days = request.days or 1
        pdf_buffer = generate_pdf(request.itinerary_data, destination, days)
        
        # 返回PDF文件（处理中文文件名编码）
        filename = f"{destination}_{days}天行程.pdf"
        ascii_filename, utf8_encoded = safe_filename_for_header(filename)
        return Response(
            content=pdf_buffer.read(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{utf8_encoded}'
            }
        )
    except json.JSONDecodeError as e:
        logger.error(f"PDF生成失败 - JSON解析错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: 行程数据格式错误 - {str(e)}"
        )
    except Exception as e:
        logger.error(f"PDF生成失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF生成失败: {str(e)}"
        )


# ============ Share Endpoints ============
@app.post("/api/itinerary/{itinerary_id}/share")
async def create_share_link(
    itinerary_id: int,
    request: CreateShareLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建分享链接"""
    # 验证行程属于当前用户
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    # 检查是否已存在分享链接
    existing_share = db.query(ShareLink).filter(
        ShareLink.itinerary_id == itinerary_id
    ).first()
    
    if existing_share:
        # 更新现有分享链接
        existing_share.is_public = 1 if request.is_public else 0
        if request.expires_days:
            existing_share.expires_at = datetime.utcnow() + timedelta(days=request.expires_days)
        else:
            existing_share.expires_at = None
        db.commit()
        db.refresh(existing_share)
        return {
            "share_token": existing_share.share_token,
            "share_url": f"/share/{existing_share.share_token}",
            "is_public": existing_share.is_public == 1,
            "expires_at": str(existing_share.expires_at) if existing_share.expires_at else None
        }
    
    # 生成唯一的分享token
    while True:
        share_token = secrets.token_urlsafe(32)
        if not db.query(ShareLink).filter(ShareLink.share_token == share_token).first():
            break
    
    # 计算过期时间
    expires_at = None
    if request.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_days)
    
    # 创建分享链接
    share_link = ShareLink(
        itinerary_id=itinerary_id,
        share_token=share_token,
        is_public=1 if request.is_public else 0,
        expires_at=expires_at
    )
    db.add(share_link)
    db.commit()
    db.refresh(share_link)
    
    return {
        "share_token": share_link.share_token,
        "share_url": f"/share/{share_link.share_token}",
        "is_public": share_link.is_public == 1,
        "expires_at": str(share_link.expires_at) if share_link.expires_at else None
    }


@app.post("/api/share/temporary")
async def create_temporary_share(
    request: CreateTemporaryShareRequest,
    db: Session = Depends(get_db)
):
    """创建临时分享链接（用于游客用户）"""
    # 生成唯一的分享token
    while True:
        share_token = secrets.token_urlsafe(32)
        if not db.query(ShareLink).filter(ShareLink.share_token == share_token).first() and \
           not db.query(TemporaryShare).filter(TemporaryShare.share_token == share_token).first():
            break
    
    # 计算过期时间
    expires_at = datetime.utcnow() + timedelta(days=request.expires_days)
    
    # 创建临时分享
    temporary_share = TemporaryShare(
        share_token=share_token,
        itinerary_data=json.dumps(request.itinerary_data, ensure_ascii=False),
        expires_at=expires_at
    )
    db.add(temporary_share)
    db.commit()
    db.refresh(temporary_share)
    
    return {
        "share_token": temporary_share.share_token,
        "share_url": f"/share/{temporary_share.share_token}",
        "expires_at": str(temporary_share.expires_at)
    }


@app.get("/api/share/{share_token}")
async def get_shared_itinerary(
    share_token: str,
    db: Session = Depends(get_db)
):
    """获取分享的行程（无需登录，支持永久分享和临时分享）"""
    # 先尝试查找永久分享
    share_link = db.query(ShareLink).filter(ShareLink.share_token == share_token).first()
    
    if share_link:
        # 检查是否过期
        if share_link.expires_at and datetime.utcnow() > share_link.expires_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="分享链接已过期"
            )
        
        # 获取行程
        itinerary = db.query(Itinerary).filter(Itinerary.id == share_link.itinerary_id).first()
        
        if not itinerary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="行程不存在"
            )
        
        # 解析行程数据
        itinerary_data = json.loads(itinerary.itinerary_data)
        
        return {
            "id": itinerary.id,
            "destination": itinerary.destination,
            "days": itinerary.days,
            "created_at": str(itinerary.created_at),
            "itinerary_data": itinerary_data,
            "share_info": {
                "is_public": share_link.is_public == 1,
                "expires_at": str(share_link.expires_at) if share_link.expires_at else None,
                "is_temporary": False
            }
        }
    
    # 尝试查找临时分享
    temporary_share = db.query(TemporaryShare).filter(TemporaryShare.share_token == share_token).first()
    
    if temporary_share:
        # 检查是否过期
        if datetime.utcnow() > temporary_share.expires_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="分享链接已过期"
            )
        
        # 解析行程数据
        itinerary_data = json.loads(temporary_share.itinerary_data)
        
        # 从行程数据中提取基本信息
        # 目的地可能在顶层，也可能在请求参数中（如果前端传递了）
        destination = itinerary_data.get("destination") or "未知目的地"
        # 天数从dailyPlans的长度推断
        days = len(itinerary_data.get("dailyPlans", [])) or 1
        
        return {
            "id": None,
            "destination": destination,
            "days": days,
            "created_at": str(temporary_share.created_at),
            "itinerary_data": itinerary_data,
            "share_info": {
                "is_public": True,
                "expires_at": str(temporary_share.expires_at),
                "is_temporary": True
            }
        }
    
    # 都没找到
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="分享链接不存在"
    )


# ============ Favorite Endpoints ============
@app.post("/api/favorites/{itinerary_id}")
async def add_favorite(
    itinerary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏行程"""
    # 验证行程属于当前用户
    itinerary = db.query(Itinerary).filter(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == current_user.id
    ).first()
    
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="行程不存在或无权限访问"
        )
    
    # 检查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.itinerary_id == itinerary_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该行程已收藏"
        )
    
    # 添加收藏
    favorite = Favorite(
        user_id=current_user.id,
        itinerary_id=itinerary_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return {"message": "收藏成功", "favorite_id": favorite.id}


@app.delete("/api/favorites/{itinerary_id}")
async def remove_favorite(
    itinerary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.itinerary_id == itinerary_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未收藏该行程"
        )
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "取消收藏成功"}


@app.get("/api/favorites")
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """获取收藏列表"""
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).order_by(Favorite.created_at.desc()).limit(limit).offset(offset).all()
    
    total = db.query(Favorite).filter(Favorite.user_id == current_user.id).count()
    
    # 获取收藏的行程信息
    items = []
    for fav in favorites:
        itinerary = db.query(Itinerary).filter(Itinerary.id == fav.itinerary_id).first()
        if itinerary:
            items.append({
                "id": itinerary.id,
                "destination": itinerary.destination,
                "days": itinerary.days,
                "budget": itinerary.budget,
                "created_at": str(itinerary.created_at),
                "favorite_id": fav.id,
                "favorited_at": str(fav.created_at),
                "preview": {
                    "agentName": itinerary.agent_name,
                    "travelers": itinerary.travelers,
                    "totalBudget": itinerary.total_budget
                }
            })
    
    return {
        "total": total,
        "items": items
    }


@app.get("/api/favorites/{itinerary_id}/status")
async def get_favorite_status(
    itinerary_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查行程是否已收藏"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.itinerary_id == itinerary_id
    ).first()
    
    return {"is_favorited": favorite is not None}


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
