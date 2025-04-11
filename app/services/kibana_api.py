# app/services/kibana_api.py

import json
import requests
import logging

logger = logging.getLogger(__name__)

def get_dashboards(kibana_url, username, password):
    endpoint = f"{kibana_url}/api/saved_objects/_find"
    params = {
        "type": "dashboard",
        "per_page": 1000  # Adjust if you have many dashboards
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(
            endpoint,
            headers=headers,
            params=params,
            auth=(username, password),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        dashboards = []
        for saved_object in data.get("saved_objects", []):
            dashboards.append({
                "id": saved_object["id"],
                "title": saved_object["attributes"].get("title", "Untitled Dashboard")
            })
        return dashboards

    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching dashboards: {http_err}")
        raise
    except Exception as err:
        logger.error(f"An error occurred while fetching dashboards: {err}")
        raise


def get_dashboard_panels(kibana_url, username, password, dashboard_id):
    endpoint = f"{kibana_url}/api/saved_objects/dashboard/{dashboard_id}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(
            endpoint,
            headers=headers,
            auth=(username, password),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        panels_list = json.loads(data["attributes"]["panelsJSON"])
        panels = []
        for panel in panels_list:
            panels.append({
                "id": panel.get("panelIndex"),
                "title": panel.get("title") or panel.get("embeddableConfig", {}).get("attributes", {}).get("title", "Panel_Title_Not_Available")
            })

        return panels
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching dashboard: {http_err}")
        raise
    except Exception as err:
        logger.error(f"An error occurred while fetching dashboard: {err}")
        raise
