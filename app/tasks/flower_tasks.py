from crewai import Task, Agent
from app.prompts import (
    flower_analysis_description, FLOWER_ANALYSIS_EXPECTED_OUTPUT,
    BOUQUET_STYLING_DESCRIPTION, BOUQUET_STYLING_EXPECTED_OUTPUT,
    shop_matching_description, SHOP_MATCHING_EXPECTED_OUTPUT,
)


def create_flower_analysis_task(agent: Agent, user_situation: str) -> Task:
    return Task(
        description=flower_analysis_description(user_situation),
        expected_output=FLOWER_ANALYSIS_EXPECTED_OUTPUT,
        agent=agent,
    )


def create_bouquet_styling_task(agent: Agent, flower_analysis_task: Task) -> Task:
    return Task(
        description=BOUQUET_STYLING_DESCRIPTION,
        expected_output=BOUQUET_STYLING_EXPECTED_OUTPUT,
        agent=agent,
        context=[flower_analysis_task],
    )


def create_shop_matching_task(agent: Agent, location: str, flower_names: str) -> Task:
    return Task(
        description=shop_matching_description(location, flower_names),
        expected_output=SHOP_MATCHING_EXPECTED_OUTPUT,
        agent=agent,
    )
