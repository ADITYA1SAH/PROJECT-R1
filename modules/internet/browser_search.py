"""
Real browser search using Playwright (DuckDuckGo HTML)
"""

from playwright.sync_api import sync_playwright
import time


def search_duckduckgo(query):
    """
    Perform a search using DuckDuckGo HTML (no blocking).
    Returns the first result.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to DuckDuckGo HTML
            page.goto("https://html.duckduckgo.com/html/", timeout=10000)
            
            # Type the query
            page.fill('input[name="q"]', query)
            page.keyboard.press("Enter")
            
            # Wait for results
            page.wait_for_selector('.result', timeout=10000)
            
            # Get the first result
            first_result = page.query_selector('.result__a')
            if first_result:
                result_text = first_result.inner_text()
                browser.close()
                return result_text
            
            browser.close()
            return "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"