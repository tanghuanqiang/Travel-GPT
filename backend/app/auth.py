"""
认证相关功能
包括密码加密、JWT token 生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import random
import string
from .database import get_db
from .db_models import User, EmailVerification
from .email_utils import send_email

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "your-secret-key-here-change-in-production"  # 生产环境应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# HTTP Bearer 认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 检查token是否过期
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token缺少过期时间",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证token未过期
        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期，请重新登录",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except JWTError as e:
        print(f"JWT解码错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户（依赖注入）"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    
    # 转换字符串 ID 为整数
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，用于不强制登录的接口）"""
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def generate_verification_code(length: int = 6) -> str:
    """生成指定长度的随机验证码"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def send_verification_email(email: str, code: str) -> None:
    """发送注册验证码邮件"""
    subject = "📧 Travel-GPT 邮箱验证码"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h1 style="color: #2563eb;">Travel-GPT 注册验证码</h1>
        <p>您好，</p>
        <p>感谢您注册 Travel-GPT！</p>
        <p>您的验证码是：<strong style="font-size: 24px; color: #2563eb;">{code}</strong></p>
        <p>验证码有效期为 <strong>5分钟</strong>，请尽快完成验证。</p>
        <p>如果您没有请求此验证码，请忽略此邮件。</p>
        <br>
        <p>祝您使用愉快！</p>
        <p>Travel-GPT Team</p>
    </body>
    </html>
    """
    send_email(email, subject, html_body)


def create_verification_code(db: Session, email: str) -> str:
    """创建并发送验证码"""
    # 检查是否已有验证码记录
    existing = db.query(EmailVerification).filter(EmailVerification.email == email).first()
    if existing:
        # 删除旧验证码
        db.delete(existing)
        db.commit()
    
    # 生成新验证码
    code = generate_verification_code()
    
    # 计算过期时间（5分钟后）
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # 创建新的验证码记录
    verification = EmailVerification(
        email=email,
        verification_code=code,
        expires_at=expires_at
    )
    
    db.add(verification)
    db.commit()
    
    # 发送验证码邮件
    send_verification_email(email, code)
    
    return code


def verify_verification_code(db: Session, email: str, code: str) -> bool:
    """验证验证码是否有效"""
    # 查找验证码记录
    verification = db.query(EmailVerification).filter(EmailVerification.email == email).first()
    
    if not verification:
        return False
    
    # 检查验证码是否过期
    if datetime.utcnow() > verification.expires_at:
        # 删除过期的验证码
        db.delete(verification)
        db.commit()
        return False
    
    # 检查验证码是否匹配
    if verification.verification_code == code:
        # 验证成功，删除验证码
        db.delete(verification)
        db.commit()
        return True
    
    return False


def send_reset_password_email(email: str, code: str) -> None:
    """发送重置密码验证码邮件"""
    subject = "🔒 Travel-GPT 密码重置验证码"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h1 style="color: #2563eb;">Travel-GPT 密码重置</h1>
        <p>您好，</p>
        <p>您请求重置 Travel-GPT 账号的密码。</p>
        <p>您的重置密码验证码是：<strong style="font-size: 24px; color: #2563eb;">{code}</strong></p>
        <p>验证码有效期为 <strong>5分钟</strong>，请尽快完成密码重置。</p>
        <p>如果您没有请求此验证码，请忽略此邮件，您的账号安全不会受到影响。</p>
        <br>
        <p>祝您使用愉快！</p>
        <p>Travel-GPT Team</p>
    </body>
    </html>
    """
    send_email(email, subject, html_body)


def create_reset_password_code(db: Session, email: str) -> str:
    """创建并发送重置密码验证码"""
    # 检查用户是否存在
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邮箱未注册"
        )
    
    # 检查是否已有验证码记录
    existing = db.query(EmailVerification).filter(EmailVerification.email == email).first()
    if existing:
        # 删除旧验证码
        db.delete(existing)
        db.commit()
    
    # 生成新验证码
    code = generate_verification_code()
    
    # 计算过期时间（5分钟后）
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # 创建新的验证码记录
    verification = EmailVerification(
        email=email,
        verification_code=code,
        expires_at=expires_at
    )
    
    db.add(verification)
    db.commit()
    
    # 发送验证码邮件
    send_reset_password_email(email, code)
    
    return code


def update_user_password(db: Session, email: str, new_password: str) -> User:
    """更新用户密码"""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新密码
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    
    return user
