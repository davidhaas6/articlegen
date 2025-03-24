import unittest
import os
import tempfile
import shutil
import xml.etree.ElementTree as ET
import sys

sys.path.append('../')
from src.sitemap_generator import SitemapGenerator, SitemapConfig, PageEntry


class TestSitemapGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create some test HTML files
        os.makedirs(os.path.join(self.test_dir, "article"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "edition"), exist_ok=True)
        
        # Create index.html
        with open(os.path.join(self.test_dir, "index.html"), "w") as f:
            f.write("<html><body>Index</body></html>")
            
        # Create article files
        with open(os.path.join(self.test_dir, "article", "article1.html"), "w") as f:
            f.write("<html><body>Article 1</body></html>")
        with open(os.path.join(self.test_dir, "article", "article2.html"), "w") as f:
            f.write("<html><body>Article 2</body></html>")
            
        # Create edition file
        with open(os.path.join(self.test_dir, "edition", "1.html"), "w") as f:
            f.write("<html><body>Edition 1</body></html>")
            
        # Create special pages
        with open(os.path.join(self.test_dir, "subscribe.html"), "w") as f:
            f.write("<html><body>Subscribe</body></html>")
        with open(os.path.join(self.test_dir, "qr.html"), "w") as f:
            f.write("<html><body>QR Code</body></html>")
            
        # Base URL for tests
        self.base_url = "https://example.com/"
        
    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
        
    def test_sitemap_generation(self):
        # Create a sitemap generator
        generator = SitemapGenerator(self.base_url, self.test_dir)
        
        # Generate the sitemap
        sitemap_path = generator.generate_sitemap()
        
        # Check that the sitemap file was created
        self.assertTrue(os.path.exists(sitemap_path))
        
        # Parse the sitemap XML
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Check that the sitemap has the correct number of URLs
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        self.assertEqual(len(urls), 6)  # 6 HTML files
        
        # Check that all expected URLs are in the sitemap
        expected_paths = [
            "",  # index.html -> root URL
            "article/article1",
            "article/article2",
            "edition/1",
            "subscribe",
            "qr"
        ]
        
        found_paths = []
        for url in urls:
            loc_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            self.assertIsNotNone(loc_elem, "Location element not found in URL")
            self.assertIsNotNone(loc_elem.text, "Location text is None")
            loc = loc_elem.text
            # Remove the base URL to get the path
            path = loc.replace(self.base_url, "")
            found_paths.append(path)
            
        for path in expected_paths:
            self.assertIn(path, found_paths)
            
    def test_priority_assignment(self):
        # Create a sitemap generator
        generator = SitemapGenerator(self.base_url, self.test_dir)
        
        # Generate the sitemap
        sitemap_path = generator.generate_sitemap()
        
        # Parse the sitemap XML
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Check priorities for different page types
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        
        for url in urls:
            loc_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            priority_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
            
            self.assertIsNotNone(loc_elem, "Location element not found in URL")
            self.assertIsNotNone(priority_elem, "Priority element not found in URL")
            self.assertIsNotNone(loc_elem.text, "Location text is None")
            self.assertIsNotNone(priority_elem.text, "Priority text is None")
            
            loc = loc_elem.text
            priority = float(priority_elem.text)
            
            if loc == self.base_url:  # index (root URL)
                self.assertEqual(priority, 1.0)
            elif "article/" in loc:
                self.assertEqual(priority, 0.8)
            elif "edition/" in loc:
                self.assertEqual(priority, 0.6)
            elif loc.endswith("subscribe") or loc.endswith("qr"):
                self.assertEqual(priority, 0.5)
                
    def test_changefreq_assignment(self):
        # Create a sitemap generator
        generator = SitemapGenerator(self.base_url, self.test_dir)
        
        # Generate the sitemap
        sitemap_path = generator.generate_sitemap()
        
        # Parse the sitemap XML
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Check change frequencies for different page types
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        
        for url in urls:
            loc_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            changefreq_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
            
            self.assertIsNotNone(loc_elem, "Location element not found in URL")
            self.assertIsNotNone(changefreq_elem, "Change frequency element not found in URL")
            self.assertIsNotNone(loc_elem.text, "Location text is None")
            self.assertIsNotNone(changefreq_elem.text, "Change frequency text is None")
            
            loc = loc_elem.text
            changefreq = changefreq_elem.text
            
            if loc == self.base_url:  # index (root URL)
                self.assertEqual(changefreq, "daily")
            elif "article/" in loc:
                self.assertEqual(changefreq, "weekly")
            elif "edition/" in loc:
                self.assertEqual(changefreq, "monthly")
            elif loc.endswith("subscribe") or loc.endswith("qr"):
                self.assertEqual(changefreq, "monthly")
                
    def test_custom_config(self):
        # Create a custom configuration
        config = SitemapConfig(
            default_changefreq="yearly",
            default_priority=0.3,
            page_priorities={
                "index.html": 0.9,
                "article/": 0.7,
            },
            page_changefreqs={
                "index.html": "hourly",
                "article/": "daily",
            }
        )
        
        # Create a sitemap generator with the custom config
        generator = SitemapGenerator(self.base_url, self.test_dir, config)
        
        # Generate the sitemap
        sitemap_path = generator.generate_sitemap()
        
        # Parse the sitemap XML
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Check that the custom configuration was applied
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        
        for url in urls:
            loc_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            priority_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}priority")
            changefreq_elem = url.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq")
            
            self.assertIsNotNone(loc_elem, "Location element not found in URL")
            self.assertIsNotNone(priority_elem, "Priority element not found in URL")
            self.assertIsNotNone(changefreq_elem, "Change frequency element not found in URL")
            self.assertIsNotNone(loc_elem.text, "Location text is None")
            self.assertIsNotNone(priority_elem.text, "Priority text is None")
            self.assertIsNotNone(changefreq_elem.text, "Change frequency text is None")
            
            loc = loc_elem.text
            priority = float(priority_elem.text)
            changefreq = changefreq_elem.text
            
            if loc == self.base_url:  # index (root URL)
                self.assertEqual(priority, 0.9)
                self.assertEqual(changefreq, "hourly")
            elif "article/" in loc:
                self.assertEqual(priority, 0.7)
                self.assertEqual(changefreq, "daily")
            else:
                self.assertEqual(priority, 0.3)
                self.assertEqual(changefreq, "yearly")


if __name__ == "__main__":
    unittest.main()
