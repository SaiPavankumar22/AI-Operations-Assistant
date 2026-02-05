from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.client import LLMClient


class PlannerAgent:

    def __init__(self):
        self.llm = LLMClient()

    def create_plan(self, user_task: str) -> Dict[str, Any]:
        system_prompt = """
You are a task planning agent. Your job is to analyze user requests and create a precise execution plan.

====================
AVAILABLE TOOLS
====================

WEATHER TOOL
- tool name: weather
- function: get_current_weather
  parameters:
    - city (string, REQUIRED): City name, e.g. "Paris"
    - units (string, optional): metric | imperial | standard

- function: get_weather_forecast
  parameters:
    - city (string, REQUIRED)
    - units (string, optional)

- function: get_weather_by_coordinates
  parameters:
    - lat (number, REQUIRED)
    - lon (number, REQUIRED)
    - units (string, optional)

GITHUB TOOL
- tool name: github
- function: search_repositories
  parameters:
    - query (string, REQUIRED)
    - sort (string, optional)
    - limit (integer, optional)

NEWS TOOL
- tool name: news
- function: search_news
  parameters:
    - query (string, REQUIRED)
    - from_date (string, optional, YYYY-MM-DD)
    - sort_by (string, optional: relevancy | popularity | publishedAt)


SERP TOOL
- tool name: serp
- function: search
  parameters:
    - query (string, REQUIRED)

====================
JSON SCHEMA
====================
{
  "task_understanding": "Brief summary of user intent",
  "required_tools": ["list", "of", "tool", "names"],
  "steps": [
    {
      "step_number": 1,
      "action": "Description of what to do",
      "tool": "tool_name",
      "function": "function_name",
      "parameters": {
        "param": "value"
      },
      "reasoning": "Why this step is required"
    }
  ],
  "expected_output": "Description of the final output"
}

====================
CRITICAL RULES
====================
- You MUST use EXACT parameter names as defined above
- For weather.get_current_weather, you MUST use "city" (NOT location)
- Do NOT invent new parameter names
- Do NOT include parameters not listed in the schema
- Return ONLY valid JSON (no markdown, no explanation)
- If the user provides a city name, always prefer weather.get_current_weather
- Use metric units unless the user explicitly asks otherwise
- EVERY step MUST use a valid tool (never use "none")
- Do NOT add steps for manual processing or sorting
- If sorting or filtering is required, it MUST be handled inside a tool call


====================
EXAMPLE
====================
User Task: "What is the weather in Paris?"

Correct JSON Output:
{
  "task_understanding": "Get current weather for Paris",
  "required_tools": ["weather"],
  "steps": [
    {
      "step_number": 1,
      "action": "Retrieve current weather for Paris",
      "tool": "weather",
      "function": "get_current_weather",
      "parameters": {
        "city": "Paris",
        "units": "metric"
      },
      "reasoning": "The user wants the current weather in Paris"
    }
  ],
  "expected_output": "Current weather details for Paris"
}
"""

        user_message = f"""
User Task: {user_task}

Create the execution plan now.
"""

        try:
            plan = self.llm.generate_json(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.2
            )

            if not self._validate_plan(plan):
                raise ValueError("Generated plan does not match required schema")

            return plan

        except Exception as e:
            return {
                "task_understanding": user_task,
                "required_tools": [],
                "steps": [],
                "expected_output": "Planning failed",
                "error": str(e)
            }

    def _validate_plan(self, plan: Dict[str, Any]) -> bool:
        
        required_fields = ["task_understanding", "required_tools", "steps", "expected_output"]
        if not all(field in plan for field in required_fields):
            return False

        if not isinstance(plan["steps"], list):
            return False

        for step in plan["steps"]:
            step_fields = ["step_number", "action", "tool", "function", "parameters"]
            if not all(field in step for field in step_fields):
                return False

        return True
