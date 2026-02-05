from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool
from tools.news_tool import NewsTool
from tools.serp_tool import SerpTool


class ExecutorAgent:
    def __init__(self):
        self.tools = {
            "github": GitHubTool(),
            "weather": WeatherTool(),
            "news": NewsTool(),
            "serp": SerpTool()
        }

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        results = {
            "task": plan.get("task_understanding", "Unknown task"),
            "steps_executed": [],
            "errors": [],
            "raw_data": {}
        }

        steps = plan.get("steps", [])

        for step in steps:
            step_number = step.get("step_number")
            step_result = self.execute_step(step)

            results["steps_executed"].append({
                "step_number": step_number,
                "action": step.get("action"),
                "tool": step.get("tool"),
                "function": step.get("function"),
                "status": "success" if not (isinstance(step_result, dict) and "error" in step_result) else "failed",
                "result": step_result
            })

            # Store raw data for verifier
            step_key = f"step_{step_number}"
            results["raw_data"][step_key] = step_result

            # Track errors
            if isinstance(step_result, dict) and "error" in step_result:
                results["errors"].append({
                    "step": step_number,
                    "error": step_result["error"]
                })


        if not results["errors"] and results["raw_data"] and steps:
            last_step_key = f"step_{steps[-1].get('step_number')}"
            results["final_data"] = results["raw_data"].get(last_step_key)

        return results

    def execute_step(self, step: Dict[str, Any]) -> Any:
        tool_name = step.get("tool")
        function_name = step.get("function")
        parameters = step.get("parameters", {})

        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}

        tool = self.tools[tool_name]

        if not hasattr(tool, function_name):
            return {"error": f"Function '{function_name}' not found in tool '{tool_name}'"}

        try:
            function = getattr(tool, function_name)
            result = function(**parameters)

            # Retry once if tool returns error
            if isinstance(result, dict) and "error" in result:
                result = function(**parameters)

            return result

        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}

    def get_tool_status(self) -> Dict[str, bool]:

        return {
            "github": bool(os.environ.get("GITHUB_API_KEY")),
            "weather": bool(os.environ.get("OPENWEATHER_API_KEY")),
            "news": bool(os.environ.get("NEWS_API_KEY")),
            "serp": bool(os.environ.get("SERP_API_KEY"))
        }
