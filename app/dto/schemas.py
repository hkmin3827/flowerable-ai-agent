from typing import Optional
from pydantic import BaseModel, Field


class ContentReq(BaseModel):
    content: str = Field(..., min_length=1, max_length=500,
                         description="사용자 자유 입력 (상황 설명 또는 지역+꽃 요청 또는 'quit' 또는 'exit')")


class FlowerItem(BaseModel):
    name: str
    floralLang: str
    role: str  # "베스트" | "메인" | "서브" | "필러"


class ShopItem(BaseModel):
    shopId: int
    shopName: str
    address: str
    district: str
    availableFlowers: list[str]


class RecommendRes(BaseModel):
    phase: str
    recommendation: Optional[str] = None
    flowers: Optional[list[FlowerItem]] = None
    shops: Optional[list[ShopItem]] = None
    message: Optional[str] = None