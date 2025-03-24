#!/usr/bin/env python3
"""
Sitemap Generator

This module provides functionality to generate XML sitemaps for the Rat News Network site.
It scans the generated site directory, identifies all HTML pages, and creates a
standards-compliant sitemap.xml file.
"""

import os
import glob
from datetime import datetime
from typing import Dict, List, Optional
import logging
import xml.dom.minidom
from xml.etree import ElementTree as ET

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PageEntry:
    """Represents a single page entry in the sitemap."""

    def __init__(
        self,
        url: str,
        lastmod: Optional[datetime] = None,
        changefreq: str = "weekly",
        priority: float = 0.5,
    ):
        """
        Initialize a page entry for the sitemap.

        Args:
            url: The full URL of the page
            lastmod: Last modification date (defaults to current time if None)
            changefreq: How frequently the page changes (always, hourly, daily, weekly, monthly, yearly, never)
            priority: The priority of this URL relative to other URLs (0.0 to 1.0)
        """
        self.url = url
        self.lastmod = lastmod or datetime.now()
        self.changefreq = changefreq
        self.priority = priority


class SitemapConfig:
    """Configuration for the sitemap generator."""

    def __init__(
        self,
        default_changefreq: str = "weekly",
        default_priority: float = 0.5,
        page_priorities: Optional[Dict[str, float]] = None,
        page_changefreqs: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize sitemap configuration.

        Args:
            default_changefreq: Default change frequency for pages
            default_priority: Default priority for pages
            page_priorities: Dictionary mapping page patterns to priorities
            page_changefreqs: Dictionary mapping page patterns to change frequencies
        """
        self.default_changefreq = default_changefreq
        self.default_priority = default_priority
        self.page_priorities = page_priorities or {
            "index.html": 1.0,
            "article/": 0.8,
            "edition/": 0.6,
            "subscribe.html": 0.5,
            "qr.html": 0.5,
        }
        self.page_changefreqs = page_changefreqs or {
            "index.html": "daily",
            "article/": "weekly",
            "edition/": "monthly",
            "subscribe.html": "monthly",
            "qr.html": "monthly",
        }


class SitemapGenerator:
    """Generates XML sitemaps for the site."""

    def __init__(
        self,
        base_url: str,
        output_dir: str,
        config: Optional[SitemapConfig] = None,
    ):
        """
        Initialize the sitemap generator.

        Args:
            base_url: The base URL of the site (e.g., https://ratnewsnetwork.com/)
            output_dir: The directory containing the generated site
            config: Optional configuration for the sitemap generator
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.output_dir = output_dir
        self.config = config or SitemapConfig()

    def generate_sitemap(self) -> str:
        """
        Generate a sitemap for the site.

        Returns:
            The path to the generated sitemap.xml file
        """
        logging.info(f"Generating sitemap for {self.base_url} from {self.output_dir}")
        pages = self._discover_pages()
        sitemap_content = self._create_sitemap_xml(pages)
        sitemap_path = self._write_sitemap_file(sitemap_content)
        logging.info(f"Sitemap generated at {sitemap_path} with {len(pages)} URLs")
        return sitemap_path

    def _discover_pages(self) -> List[PageEntry]:
        """
        Discover all HTML pages in the output directory.

        Returns:
            A list of PageEntry objects representing the discovered pages
        """
        pages = []
        for html_file in glob.glob(f"{self.output_dir}/**/*.html", recursive=True):
            rel_path = os.path.relpath(html_file, self.output_dir)
            
            # Remove .html extension from the URL
            url_path = rel_path.replace(os.path.sep, "/")
            if url_path.endswith(".html"):
                url_path = url_path[:-5]  # Remove .html extension
                
            # Special case for index.html - convert to root URL
            if url_path == "index":
                url = self.base_url
            else:
                url = self.base_url + url_path
            
            # Get file modification time
            lastmod = datetime.fromtimestamp(os.path.getmtime(html_file))
            
            # Determine priority and change frequency based on the file path
            priority = self.config.default_priority
            changefreq = self.config.default_changefreq
            
            for pattern, p in self.config.page_priorities.items():
                if pattern in rel_path:
                    priority = p
                    break
                    
            for pattern, cf in self.config.page_changefreqs.items():
                if pattern in rel_path:
                    changefreq = cf
                    break
            
            pages.append(PageEntry(url, lastmod, changefreq, priority))
        
        return pages

    def _create_sitemap_xml(self, pages: List[PageEntry]) -> str:
        """
        Create the XML content for the sitemap.

        Args:
            pages: List of PageEntry objects to include in the sitemap

        Returns:
            The XML content of the sitemap as a string
        """
        # Create the root element
        urlset = ET.Element(
            "urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        )
        
        # Add each page to the sitemap
        for page in pages:
            url_element = ET.SubElement(urlset, "url")
            
            loc = ET.SubElement(url_element, "loc")
            loc.text = page.url
            
            lastmod = ET.SubElement(url_element, "lastmod")
            lastmod.text = page.lastmod.strftime("%Y-%m-%d")
            
            changefreq = ET.SubElement(url_element, "changefreq")
            changefreq.text = page.changefreq
            
            priority = ET.SubElement(url_element, "priority")
            priority.text = str(page.priority)
        
        # Convert to string with pretty formatting
        rough_string = ET.tostring(urlset, "utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def _write_sitemap_file(self, content: str) -> str:
        """
        Write the sitemap content to a file.

        Args:
            content: The XML content of the sitemap

        Returns:
            The path to the written sitemap file
        """
        sitemap_path = os.path.join(self.output_dir, "sitemap.xml")
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(content)
        return sitemap_path


def generate_sitemap(base_url: str, site_dir: str) -> str:
    """
    Convenience function to generate a sitemap.

    Args:
        base_url: The base URL of the site
        site_dir: The directory containing the generated site

    Returns:
        The path to the generated sitemap.xml file
    """
    generator = SitemapGenerator(base_url, site_dir)
    return generator.generate_sitemap()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a sitemap for a static site")
    parser.add_argument("base_url", help="The base URL of the site")
    parser.add_argument("site_dir", help="The directory containing the generated site")
    args = parser.parse_args()

    generate_sitemap(args.base_url, args.site_dir)
