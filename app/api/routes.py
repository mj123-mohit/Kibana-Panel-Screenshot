# app/api/routes.py

from fastapi import APIRouter, HTTPException
from app.config import settings
from app.services.kibana_api import get_dashboards, get_dashboard_panels
from app.services.screenshot import take_panel_screenshot
import os
import sys 
import subprocess

router = APIRouter()

@router.get("/dashboards")
def list_dashboards():
    """
    Returns a list of dashboards from Kibana.
    """
    try:
        dashboards = get_dashboards(
            kibana_url=settings.KIBANA_URL,
            username=settings.USERNAME,
            password=settings.PASSWORD
        )
        return {"dashboards": dashboards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboards/{dashboard_id}/panels")
def list_dashboard_panels(dashboard_id: str):
    """
    Returns the panels for a given dashboard.
    """
    try:
        panels = get_dashboard_panels(
            kibana_url=settings.KIBANA_URL,
            username=settings.USERNAME,
            password=settings.PASSWORD,
            dashboard_id=dashboard_id
        )
        return {"dashboard_id": dashboard_id, "panels": panels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboards/{dashboard_id}/panels/{panel_id}/screenshot")
def screenshot_panel(dashboard_id: str, panel_id: str):
    """
    Invokes the screenshot_cli.py script via subprocess to capture a Kibana panel screenshot.
    """
    # Create output directory if it doesn't exist
    screenshot_dir = settings.OUTPUT_DIR or "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    # Build the path/filename for the screenshot
    screenshot_filename = f"dashboard_{dashboard_id}_panel_{panel_id}.png"
    screenshot_path = os.path.join(screenshot_dir, screenshot_filename)

    # Build the CLI command to run
    # Note: Adjust the relative path to screenshot_cli.py depending on your project layout
    cli_args = [
        sys.executable,               
        "app/services/screenshot_cli.py",
        "--kibana-url", settings.KIBANA_URL,
        "--username", settings.USERNAME,
        "--password", settings.PASSWORD,
        "--dashboard-id", dashboard_id,
        "--panel-identifier", panel_id,
        "--screenshot-path", screenshot_path
    ]

    try:
        # Run the command and capture output
        result = subprocess.run(cli_args, capture_output=True, text=True)
        
        # Check if the process ended with an error
        if result.returncode != 0:
            # Pass along stderr to the HTTPException for easier debugging
            raise RuntimeError(f"CLI Error: {result.stderr}")

        return {"detail": f"Screenshot saved to {screenshot_path}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
