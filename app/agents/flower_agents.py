from crewai import Agent
from app.tools.flower_tools import (
    get_flowers_by_sentiment,
    get_matching_sub_flowers,
    get_shops_by_location_and_flower,
)
from app.core.model import model
from app.prompts import FLORAL_ANALYST_PROMPTS, BOUQUET_STYLING_PROMPTS, LOCAL_SHOP_MATCHER_PROMPTS

def create_floral_analyst() -> Agent:
    return Agent(
        role=FLORAL_ANALYST_PROMPTS["role"],
        goal=FLORAL_ANALYST_PROMPTS["goal"],
        backstory=FLORAL_ANALYST_PROMPTS["backstory"],
        tools=[get_flowers_by_sentiment],
        llm=model,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def create_bouquet_stylist() -> Agent:
    return Agent(
        role=BOUQUET_STYLING_PROMPTS["role"],
        goal=BOUQUET_STYLING_PROMPTS["goal"],
        backstory=BOUQUET_STYLING_PROMPTS["backstory"],
        tools=[get_matching_sub_flowers],
        llm=model,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def create_local_shop_matcher() -> Agent:
    return Agent(
        role=LOCAL_SHOP_MATCHER_PROMPTS["role"],
        goal=LOCAL_SHOP_MATCHER_PROMPTS["goal"],
        backstory=LOCAL_SHOP_MATCHER_PROMPTS["backstory"],
        tools=[get_shops_by_location_and_flower],
        llm=model,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )
