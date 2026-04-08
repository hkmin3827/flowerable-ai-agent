from crewai import Task, Agent
from app.prompts import (
    _flower_analysis_description, _FLOWER_ANALYSIS_EXPECTED_OUTPUT,
    _BOUQUET_STYLING_DESCRIPTION, _BOUQUET_STYLING_EXPECTED_OUTPUT,
    _shop_matching_description, _SHOP_MATCHING_EXPECTED_OUTPUT,
    _location_parsing_description, _LOCATION_PARSING_EXPECTED_OUTPUT,
)

def create_flower_analysis_task(agent: Agent, user_situation: str) -> Task:
    return Task(
        description=_flower_analysis_description(user_situation),
        expected_output=_FLOWER_ANALYSIS_EXPECTED_OUTPUT,
        agent=agent,
    )


def create_bouquet_styling_task(agent: Agent, flower_analysis_task: Task) -> Task:
    return Task(
        description=_BOUQUET_STYLING_DESCRIPTION,
        expected_output=_BOUQUET_STYLING_EXPECTED_OUTPUT,
        agent=agent,
        context=[flower_analysis_task],
    )

def create_shop_matching_task(agent: Agent, location: str, flower_names: str,
                              address_hint: str = "") -> Task:
    tool_input = f"{location}|{flower_names}"
    if address_hint:
        tool_input = f"{tool_input}|{address_hint}"

    return Task(
        description=_shop_matching_description(location, flower_names),
        expected_output=_SHOP_MATCHING_EXPECTED_OUTPUT,
        agent=agent,
    )


def create_location_parsing_task(agent: Agent, user_content: str) -> Task:
    return Task(
        description=_location_parsing_description(user_content),
        expected_output=_LOCATION_PARSING_EXPECTED_OUTPUT,
        agent=agent,
    )
