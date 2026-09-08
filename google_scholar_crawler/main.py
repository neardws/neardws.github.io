#!/usr/bin/env python3
"""
Google Scholar Citation Data Crawler

This script fetches author citation data from Google Scholar.
It includes timeout handling and retry limits to prevent long-running jobs.
"""

from scholarly import scholarly
import json
from datetime import datetime
import os
import sys
import signal

# Configuration
REQUEST_TIMEOUT = 300  # 5 minutes total timeout for the entire operation
MAX_RETRIES = 3        # Maximum retry attempts for each request
RETRY_DELAY = 10       # Seconds to wait between retries

# Global timeout handler
def timeout_handler(signum, frame):
    print("ERROR: Operation timed out after {} seconds".format(REQUEST_TIMEOUT))
    sys.exit(1)

# Set up signal-based timeout (only works on Unix-like systems)
if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(REQUEST_TIMEOUT)

def fetch_author_data(scholar_id: str) -> dict:
    """
    Fetch author data from Google Scholar with retry logic.
    
    Args:
        scholar_id: Google Scholar author ID
        
    Returns:
        dict: Author data including citations and publications
    """
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Fetching author data...")
            
            # Search for author by ID
            author = scholarly.search_author_id(scholar_id)
            
            # Fill author data - only get essentials to reduce requests
            # Removed 'publications' section as it requires many additional requests
            scholarly.fill(author, sections=['basics', 'indices', 'counts'])
            
            print(f"Successfully fetched data for: {author.get('name', 'Unknown')}")
            return author
            
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                import time
                time.sleep(RETRY_DELAY)
    
    # All retries failed
    raise Exception(f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}")

def main():
    """Main entry point."""
    scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
    
    if not scholar_id:
        print("ERROR: GOOGLE_SCHOLAR_ID environment variable is not set")
        sys.exit(1)
    
    print(f"Starting Google Scholar data fetch for ID: {scholar_id}")
    print(f"Timeout: {REQUEST_TIMEOUT} seconds, Max retries: {MAX_RETRIES}")
    
    try:
        # Fetch author data
        author = fetch_author_data(scholar_id)
        
        # Add timestamp
        author['updated'] = str(datetime.now())
        
        # Print summary
        print("\n=== Author Summary ===")
        print(f"Name: {author.get('name', 'N/A')}")
        print(f"Citations: {author.get('citedby', 'N/A')}")
        print(f"h-index: {author.get('hindex', 'N/A')}")
        print(f"i10-index: {author.get('i10index', 'N/A')}")
        
        # Create results directory
        os.makedirs('results', exist_ok=True)
        
        # Save full data
        with open('results/gs_data.json', 'w') as outfile:
            json.dump(author, outfile, ensure_ascii=False, indent=2)
        print("\nSaved full data to results/gs_data.json")
        
        # Save shields.io format
        shieldio_data = {
            "schemaVersion": 1,
            "label": "citations",
            "message": str(author.get('citedby', 0)),
        }
        with open('results/gs_data_shieldsio.json', 'w') as outfile:
            json.dump(shieldio_data, outfile, ensure_ascii=False, indent=2)
        print("Saved shields.io data to results/gs_data_shieldsio.json")
        
        print("\n=== Done ===")
        
        # Cancel the timeout alarm on success
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
            
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
