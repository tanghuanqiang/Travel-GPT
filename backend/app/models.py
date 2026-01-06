from pydantic import BaseModel, Field
from typing import List, Optional


class TravelRequest(BaseModel):
    """旅行请求模型"""
    agentName: Optional[str] = Field(default="我的周末旅行", description="行程名称")
    destination: Optional[str] = Field(default="", description="目的地城市")
    days: Optional[int] = Field(default=2, ge=1, le=5, description="旅行天数")
    budget: Optional[str] = Field(default="", description="预算范围")
    travelers: Optional[int] = Field(default=2, ge=1, description="出行人数")
    preferences: Optional[List[str]] = Field(default=[], description="偏好标签")
    extraRequirements: Optional[str] = Field(default="", description="额外要求")


class BudgetItem(BaseModel):
    """预算项目"""
    category: str
    amount: float


class Activity(BaseModel):
    """活动项目"""
    time: str
    title: str
    description: str
    duration: str
    cost: float
    address: str
    reason: str
    images: Optional[List[str]] = []


class DailyPlan(BaseModel):
    """每日计划"""
    day: int
    title: str
    activities: List[Activity]


class HiddenGem(BaseModel):
    """隐藏宝石"""
    title: str
    description: str
    category: str


class PracticalTips(BaseModel):
    """实用建议"""
    transportation: str
    packingList: List[str]
    weather: str
    seasonalNotes: str


class BudgetOverview(BaseModel):
    """预算概览"""
    totalBudget: float
    budgetBreakdown: List[BudgetItem]


class TravelItinerary(BaseModel):
    """完整旅行行程"""
    overview: BudgetOverview
    dailyPlans: List[DailyPlan]
    hiddenGems: List[HiddenGem]
    practicalTips: PracticalTips
