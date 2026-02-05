
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import os

from dotenv import load_dotenv
load_dotenv()

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent


# Initialize FastAPI app
app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent AI system for task automation with LLM-powered reasoning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
planner = PlannerAgent()
executor = ExecutorAgent()
verifier = VerifierAgent()


# Request/Response Models
class TaskRequest(BaseModel):
    task: str
    include_raw_data: Optional[bool] = False


class TaskResponse(BaseModel):
    status: str
    task: str
    plan: Dict[str, Any]
    execution_results: Dict[str, Any]
    verification: Dict[str, Any]
    formatted_output: str


@app.get("/")
async def root():

    return {
        "message": "AI Operations Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "/process": "POST - Process a natural language task",
            "/health": "GET - Check system health",
            "/tools": "GET - List available tools",
            "/docs": "GET - API documentation (Swagger UI)"
        }
    }


@app.get("/health")
async def health_check():

    env_status = {
        "NEBIUS_API_KEY": bool(os.environ.get("NEBIUS_API_KEY")),
        "GITHUB_API_KEY": bool(os.environ.get("GITHUB_API_KEY")),
        "OPENWEATHER_API_KEY": bool(os.environ.get("OPENWEATHER_API_KEY")),
        "NEWS_API_KEY": bool(os.environ.get("NEWS_API_KEY")),
        "SERP_API_KEY": bool(os.environ.get("SERP_API_KEY"))
    }
    
    all_configured = all(env_status.values())
    
    return {
        "status": "healthy" if all_configured else "partially_configured",
        "agents": {
            "planner": "ready",
            "executor": "ready",
            "verifier": "ready"
        },
        "api_keys_configured": env_status,
        "tools_available": executor.get_tool_status()
    }


@app.get("/tools")
async def list_tools():

    return {
        "tools": {
            "github": {
                "description": "Search GitHub repositories and get repository information",
                "functions": [
                    "search_repositories - Search for repositories",
                    "get_repository - Get details of a specific repository",
                    "get_user_repos - Get repositories for a user"
                ],
                "configured": bool(os.environ.get("GITHUB_API_KEY"))
            },
            "weather": {
                "description": "Get weather information for cities worldwide",
                "functions": [
                    "get_current_weather - Get current weather for a city",
                    "get_weather_forecast - Get weather forecast",
                    "get_weather_by_coordinates - Get weather by lat/lon"
                ],
                "configured": bool(os.environ.get("OPENWEATHER_API_KEY"))
            },
            "news": {
                "description": "Search and retrieve news articles",
                "functions": [
                    "get_top_headlines - Get top headlines by country/category",
                    "search_news - Search for news articles",
                    "get_sources - Get available news sources"
                ],
                "configured": bool(os.environ.get("NEWS_API_KEY"))
            },
            "serp": {
                "description": "Perform web searches and get search results",
                "functions": [
                    "search - General web search",
                    "search_news - Search for news",
                    "search_images - Search for images",
                    "get_answer_box - Get direct answers"
                ],
                "configured": bool(os.environ.get("SERP_API_KEY"))
            }
        }
    }


@app.post("/process", response_model=TaskResponse)
async def process_task(request: TaskRequest):

    try:

        if not os.environ.get("NEBIUS_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="NEBIUS_API_KEY not configured. Please set it in .env file."
            )
        
 
        print(f"\n{'='*60}")
        print(f"Processing task: {request.task}")
        print(f"{'='*60}\n")
        
        print("Step 1: Creating execution plan...")
        plan = planner.create_plan(request.task)
        
        if "error" in plan:
            raise HTTPException(
                status_code=500,
                detail=f"Planning failed: {plan['error']}"
            )
        
        print(f"✓ Plan created with {len(plan.get('steps', []))} steps")
        

        print("\nStep 2: Executing plan...")
        execution_results = executor.execute_plan(plan)
        
        error_count = len(execution_results.get("errors", []))
        success_count = len(execution_results.get("steps_executed", [])) - error_count
        print(f"✓ Execution complete: {success_count} successful, {error_count} errors")
        

        print("\nStep 3: Verifying results...")
        verification = verifier.verify_results(
            original_task=request.task,
            execution_results=execution_results,
            plan=plan
        )
        
        print(f"✓ Verification complete: {verification.get('confidence', 'unknown')} confidence")
        

        formatted_output = verifier.format_output(verification)
        
        print("\n" + formatted_output)
        

        response = {
            "status": "complete" if verification.get("is_complete") else "partial",
            "task": request.task,
            "plan": plan,
            "execution_results": execution_results if request.include_raw_data else {
                "steps_count": len(execution_results.get("steps_executed", [])),
                "errors_count": len(execution_results.get("errors", []))
            },
            "verification": verification if request.include_raw_data else {
                "is_complete": verification.get("is_complete"),
                "confidence": verification.get("confidence"),
                "final_answer": verification.get("final_answer")
            },
            "formatted_output": formatted_output
        }
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing task: {str(e)}"
        )


@app.post("/plan")
async def create_plan_only(request: TaskRequest):
    """Create an execution plan without executing it"""
    try:
        plan = planner.create_plan(request.task)
        return {
            "status": "success",
            "task": request.task,
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Planning failed: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     AI OPERATIONS ASSISTANT - Multi-Agent System          ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    print(f"Starting server on {host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Alternative docs: http://{host}:{port}/redoc")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True, 
        log_level="info"
    )