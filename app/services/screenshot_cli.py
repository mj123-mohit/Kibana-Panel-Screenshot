#!/usr/bin/env python3

import argparse
import logging

# Import the synchronous wrapper from your screenshot.py
from screenshot import take_panel_screenshot

def main():
    parser = argparse.ArgumentParser(
        description='Take a screenshot of a specific panel on a Kibana dashboard.'
    )
    parser.add_argument('--kibana-url', required=True, help='The base URL of Kibana (e.g., https://example.com).')
    parser.add_argument('--username', required=True, help='Kibana username for logging in.')
    parser.add_argument('--password', required=True, help='Kibana password for logging in.')
    parser.add_argument('--dashboard-id', required=True, help='Kibana dashboard ID (e.g., d1234560-789a-4bcd-ef01-234567890abc).')
    parser.add_argument('--panel-identifier', required=True, help='Identifier of the panel to screenshot.')
    parser.add_argument('--screenshot-path', required=True, help='Path/filename where the screenshot will be saved.')

    args = parser.parse_args()

    # Optional: Configure logging if desired
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Call the synchronous wrapper to take the screenshot
    take_panel_screenshot(
        kibana_url=args.kibana_url,
        username=args.username,
        password=args.password,
        dashboard_id=args.dashboard_id,
        panel_identifier=args.panel_identifier,
        screenshot_path=args.screenshot_path
    )

if __name__ == '__main__':
    main()
