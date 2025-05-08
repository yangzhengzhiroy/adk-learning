"""Finance"""
from pydantic import BaseModel, Field


class Financials(BaseModel):
    name: str = Field(description="the user's name which the financial report belongs to")
    income: str = Field(description="individual income record from the financial report separated by comma")
    spending: str = Field(description="the individual spending of the user separated by comma")
    insurance: str = Field(description="the individual insurance purchased by the user separated by comma")
    investment: str = Field(description="the individual investment made by the user separated by comma")

class FinancialSummary(BaseModel):
    name: str = Field(description="the user's name which the financial report belongs to")
    income: float = Field(description="the total income of the user")
    spending: float = Field(description="the total spending of the user")
    insurance: float = Field(description="the total insurance purchased by the user")
    investment: float = Field(description="the total investment made by the user")
