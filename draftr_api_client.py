"""
Draftr API Client - Direct API Integration (No Browser Automation)

This is a HYPOTHETICAL implementation showing how to use Draftr's API
if it exists. Actual implementation depends on Draftr's real API structure.

Security: API tokens stored in Streamlit secrets (more secure than cookies)
"""

import requests
from typing import Dict, List, Optional
import streamlit as st


class DraftrAPIClient:
    """Client for interacting with Draftr API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Draftr API client
        
        Args:
            api_key: Draftr API key (or loaded from secrets)
            base_url: Draftr API base URL (default: https://api.webpub.autodesk.com/draftr)
        """
        # Get API key from secrets if not provided
        self.api_key = api_key
        if not self.api_key and hasattr(st, 'secrets') and 'DRAFTR_API_KEY' in st.secrets:
            self.api_key = st.secrets['DRAFTR_API_KEY']
        
        if not self.api_key:
            raise ValueError("No Draftr API key provided. Add DRAFTR_API_KEY to Streamlit secrets.")
        
        self.base_url = base_url or "https://api.webpub.autodesk.com/draftr/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_asset(self, asset_id: str) -> Dict:
        """
        Get asset details
        
        Args:
            asset_id: Draftr asset ID
            
        Returns:
            Asset data including content and links
        """
        url = f"{self.base_url}/assets/{asset_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_asset_links(self, asset_id: str) -> List[Dict]:
        """
        Get all links in an asset
        
        Args:
            asset_id: Draftr asset ID
            
        Returns:
            List of links with their IDs, URLs, and text
        """
        url = f"{self.base_url}/assets/{asset_id}/links"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def update_link(self, asset_id: str, link_id: str, new_url: str) -> Dict:
        """
        Update a specific link in an asset
        
        Args:
            asset_id: Draftr asset ID
            link_id: ID of the link to update
            new_url: New URL for the link
            
        Returns:
            Updated link data
        """
        url = f"{self.base_url}/assets/{asset_id}/links/{link_id}"
        data = {"url": new_url}
        response = self.session.patch(url, json=data)
        response.raise_for_status()
        return response.json()
    
    def find_and_update_link(self, asset_id: str, link_text: str, new_url: str) -> Dict:
        """
        Find a link by text and update its URL
        
        Args:
            asset_id: Draftr asset ID
            link_text: Text of the link to find
            new_url: New URL for the link
            
        Returns:
            Result with updated link info
        """
        # Get all links
        links = self.get_asset_links(asset_id)
        
        # Find link by text
        target_link = None
        for link in links:
            if link.get('text', '').lower() == link_text.lower():
                target_link = link
                break
        
        if not target_link:
            return {
                'success': False,
                'error': f'Link with text "{link_text}" not found',
                'available_links': [l.get('text') for l in links]
            }
        
        # Update the link
        updated = self.update_link(asset_id, target_link['id'], new_url)
        
        return {
            'success': True,
            'link_id': target_link['id'],
            'link_text': link_text,
            'old_url': target_link.get('url'),
            'new_url': new_url,
            'updated_at': updated.get('updated_at')
        }
    
    def bulk_replace_links(self, asset_id: str, old_url: str, new_url: str) -> Dict:
        """
        Replace all occurrences of a URL in an asset
        
        Args:
            asset_id: Draftr asset ID
            old_url: Old URL to replace
            new_url: New URL
            
        Returns:
            Result with count of updated links
        """
        links = self.get_asset_links(asset_id)
        updated_count = 0
        updated_links = []
        
        for link in links:
            if link.get('url') == old_url:
                updated = self.update_link(asset_id, link['id'], new_url)
                updated_count += 1
                updated_links.append({
                    'id': link['id'],
                    'text': link.get('text'),
                    'old_url': old_url,
                    'new_url': new_url
                })
        
        return {
            'success': True,
            'updated_count': updated_count,
            'updated_links': updated_links
        }
    
    def replace_domain(self, asset_id: str, old_domain: str, new_domain: str) -> Dict:
        """
        Replace domain in all links
        
        Args:
            asset_id: Draftr asset ID
            old_domain: Old domain to replace (e.g., '/en/')
            new_domain: New domain (e.g., '/uk/')
            
        Returns:
            Result with count of updated links
        """
        links = self.get_asset_links(asset_id)
        updated_count = 0
        updated_links = []
        
        for link in links:
            url = link.get('url', '')
            if old_domain in url:
                new_url = url.replace(old_domain, new_domain)
                updated = self.update_link(asset_id, link['id'], new_url)
                updated_count += 1
                updated_links.append({
                    'id': link['id'],
                    'text': link.get('text'),
                    'old_url': url,
                    'new_url': new_url
                })
        
        return {
            'success': True,
            'updated_count': updated_count,
            'updated_links': updated_links
        }


# Example usage functions for Streamlit integration

def draftr_api_update_link(asset_id: str, link_text: str, new_url: str) -> Dict:
    """
    Streamlit-friendly function to update a Draftr link via API
    
    Args:
        asset_id: Draftr asset ID
        link_text: Text of link to find
        new_url: New URL
        
    Returns:
        Result dictionary with success status and details
    """
    try:
        client = DraftrAPIClient()
        result = client.find_and_update_link(asset_id, link_text, new_url)
        return result
    except requests.HTTPError as e:
        return {
            'success': False,
            'error': f'API Error: {e.response.status_code} - {e.response.text}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }


def draftr_api_bulk_replace(asset_id: str, old_url: str, new_url: str) -> Dict:
    """
    Streamlit-friendly function to bulk replace URLs via API
    
    Args:
        asset_id: Draftr asset ID
        old_url: Old URL to replace
        new_url: New URL
        
    Returns:
        Result dictionary with success status and count
    """
    try:
        client = DraftrAPIClient()
        result = client.bulk_replace_links(asset_id, old_url, new_url)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }


def draftr_api_replace_domain(asset_id: str, old_domain: str, new_domain: str) -> Dict:
    """
    Streamlit-friendly function to replace domains via API
    
    Args:
        asset_id: Draftr asset ID
        old_domain: Old domain pattern
        new_domain: New domain pattern
        
    Returns:
        Result dictionary with success status and count
    """
    try:
        client = DraftrAPIClient()
        result = client.replace_domain(asset_id, old_domain, new_domain)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }

