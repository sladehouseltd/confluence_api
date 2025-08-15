#!/usr/bin/env python3

import argparse
import csv
import os
import sys
from datetime import datetime
from getpass import getpass
from typing import List, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth


class ConfluencePageAnalyzer:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def get_all_pages_in_space(self, space_key: str) -> List[Dict]:
        """Retrieve all pages from a Confluence space."""
        pages = []
        start = 0
        limit = 50
        
        print("Fetching pages from Confluence...")
        while True:
            url = f"{self.base_url}/rest/api/content"
            params = {
                'spaceKey': space_key,
                'type': 'page',
                'start': start,
                'limit': limit,
                'expand': 'version,history.lastUpdated,space,_links'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            pages.extend(data['results'])
            print(f"Fetched {len(pages)} pages so far...")
            
            if len(data['results']) < limit:
                break
                
            start += limit
            
        return pages
    
    def get_page_analytics(self, page_id: str) -> Optional[Dict]:
        """Get analytics data for a specific page."""
        try:
            # Try the analytics endpoint first
            url = f"{self.base_url}/rest/api/analytics/content/{page_id}/views"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data:  # Check if data is not empty
                    return data
            
            # If analytics fails, try the audit log approach (Confluence Cloud)
            audit_url = f"{self.base_url}/rest/api/audit"
            audit_params = {
                'searchString': page_id,
                'limit': 1
            }
            audit_response = self.session.get(audit_url, params=audit_params)
            
            if audit_response.status_code == 200:
                audit_data = audit_response.json()
                if audit_data.get('results'):
                    return {'audit': audit_data['results'][0]}
            
            return None
        except Exception:
            return None
    
    def analyze_pages(self, space_key: str, include_modified: bool, include_viewed: bool) -> List[Dict]:
        """Analyze pages in a space for modification and view dates."""
        pages = self.get_all_pages_in_space(space_key)
        results = []
        total_pages = len(pages)
        print(f"Found {total_pages} pages to analyze...")
        
        for i, page in enumerate(pages, 1):
            # Construct page URL using web UI link if available, fallback to page ID
            if '_links' in page and 'webui' in page['_links']:
                page_url = f"{self.base_url}{page['_links']['webui']}"
            else:
                page_url = f"{self.base_url}/display/{page['space']['key']}/{page['id']}"
            
            page_data = {
                'page': page['title'],
                'page_url': page_url,
                'page_id': page['id']
            }
            
            if include_modified:
                # Get last modified date from version history
                if 'version' in page:
                    modified_date = page['version']['when']
                    page_data['date_modified'] = datetime.fromisoformat(
                        modified_date.replace('Z', '+00:00')
                    ).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    page_data['date_modified'] = 'N/A'
            
            if include_viewed:
                # Get last viewed date from analytics
                analytics = self.get_page_analytics(page['id'])
                if analytics:
                    if 'views' in analytics and analytics['views']:
                        # Standard analytics response
                        latest_view = max(analytics['views'], key=lambda x: x['date'])
                        page_data['date_viewed'] = latest_view['date']
                    elif 'audit' in analytics:
                        # Audit log response
                        audit_entry = analytics['audit']
                        if 'creationDate' in audit_entry:
                            page_data['date_viewed'] = audit_entry['creationDate']
                        else:
                            page_data['date_viewed'] = 'N/A'
                    else:
                        # Try to use any date field available
                        for date_field in ['lastViewDate', 'lastAccessed', 'viewDate', 'date']:
                            if date_field in analytics:
                                page_data['date_viewed'] = analytics[date_field]
                                break
                        else:
                            page_data['date_viewed'] = 'N/A'
                else:
                    page_data['date_viewed'] = 'N/A'
            
            results.append(page_data)
            
            # Progress update every 50 pages
            if i % 50 == 0:
                print(f"Analyzed {i}/{total_pages} pages...")
        
        print(f"Analysis complete - processed {total_pages} pages")
        return results
    
    def write_csv(self, data: List[Dict], filename: str, include_modified: bool, include_viewed: bool):
        """Write results to CSV file."""
        if not data:
            print("No data to write.")
            return
        
        # Determine columns and sort key
        columns = ['page', 'page_url']
        sort_key = None
        
        if include_modified and include_viewed:
            columns.extend(['date_modified', 'date_viewed'])
            sort_key = 'date_modified'  # Default to modified date for sorting
        elif include_modified:
            columns.append('date_modified')
            sort_key = 'date_modified'
        elif include_viewed:
            columns.append('date_viewed')
            sort_key = 'date_viewed'
        
        # Sort data by date descending (handle N/A values)
        if sort_key:
            def sort_func(item):
                date_str = item.get(sort_key, 'N/A')
                if date_str == 'N/A':
                    return datetime.min
                try:
                    if 'T' in date_str:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return datetime.min
            
            data.sort(key=sort_func, reverse=True)
        
        # Write CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for row in data:
                # Only write columns that are defined
                filtered_row = {col: row.get(col, '') for col in columns}
                writer.writerow(filtered_row)
        
        print(f"Results written to {filename}")


def load_config():
    """Load configuration from .env file or environment variables."""
    config = {}
    
    # Try to load from .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"\'')
    
    # Override with environment variables
    config['CONFLUENCE_URL'] = os.getenv('CONFLUENCE_URL', config.get('CONFLUENCE_URL', ''))
    config['CONFLUENCE_USERNAME'] = os.getenv('CONFLUENCE_USERNAME', config.get('CONFLUENCE_USERNAME', ''))
    config['CONFLUENCE_PASSWORD'] = os.getenv('CONFLUENCE_PASSWORD', config.get('CONFLUENCE_PASSWORD', ''))
    
    return config


def get_credentials():
    """Get Confluence credentials from config or user input."""
    config = load_config()
    
    base_url = config.get('CONFLUENCE_URL', '').strip()
    username = config.get('CONFLUENCE_USERNAME', '').strip()
    password = config.get('CONFLUENCE_PASSWORD', '').strip()
    
    if not base_url:
        base_url = input("Enter Confluence URL: ").strip()
    
    if not username:
        username = input("Enter username: ").strip()
    
    if not password:
        password = getpass("Enter password: ")
    
    return base_url, username, password


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Confluence page modification and view dates'
    )
    parser.add_argument('space', help='Confluence space key')
    parser.add_argument('--date-modified', action='store_true',
                      help='Include last modified dates in output')
    parser.add_argument('--date-viewed', action='store_true',
                      help='Include last viewed dates in output')
    parser.add_argument('--output', '-o', default=None,
                      help='Output CSV filename (default: auto-generated)')
    
    args = parser.parse_args()
    
    if not args.date_modified and not args.date_viewed:
        print("Error: You must specify at least one of --date-modified or --date-viewed")
        sys.exit(1)
    
    try:
        base_url, username, password = get_credentials()
        analyzer = ConfluencePageAnalyzer(base_url, username, password)
        
        print(f"Analyzing pages in space: {args.space}")
        results = analyzer.analyze_pages(args.space, args.date_modified, args.date_viewed)
        
        if not results:
            print("No pages found in the specified space.")
            return
        
        # Generate filename if not provided
        if args.output is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"confluence_pages_{args.space}_{timestamp}.csv"
        else:
            filename = args.output
        
        analyzer.write_csv(results, filename, args.date_modified, args.date_viewed)
        print(f"Analysis complete. Found {len(results)} pages.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Confluence: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()