# Sitemap Generation

This document describes the sitemap generation process for the Rat News Network static site.

## Overview

A sitemap is an XML file that lists all the URLs of a website along with additional metadata about each URL. It helps search engines discover and index the pages of the website more efficiently. The Rat News Network site automatically generates a sitemap.xml file during the build process.

## Implementation

The sitemap generation is handled by a standalone module (`sitemap_generator.py`) that is integrated into the deployment pipeline. This approach provides several benefits:

1. **Separation of Concerns**: The sitemap generation logic is isolated from the site generation process
2. **Flexibility**: The generator can be configured with different priorities and change frequencies for different types of pages
3. **Future Compatibility**: The standalone approach makes it easier to adapt to future changes, such as a potential move to server-side rendering

## How It Works

The sitemap generator:

1. Scans the output directory for all HTML files
2. Converts file paths to URLs using the base URL
3. Assigns priorities and change frequencies based on page types
4. Generates a standards-compliant XML sitemap
5. Writes the sitemap to the output directory

## Page Priorities and Change Frequencies

Different types of pages are assigned different priorities and change frequencies:

| Page Type | Priority | Change Frequency |
|-----------|----------|------------------|
| Homepage (index.html) | 1.0 | daily |
| Article pages | 0.8 | weekly |
| Edition archive pages | 0.6 | monthly |
| Special pages (subscribe, qr) | 0.5 | monthly |

These values can be customized through the `SitemapConfig` class if needed.

## Integration with Deployment

The sitemap generator is integrated into the deployment pipeline in `deploy.py`. After the site is generated, the sitemap generator is called with the base URL and the output directory:

```python
# Generate sitemap
base_url = "https://ratnewsnetwork.com/"
sitemap_generator.generate_sitemap(base_url, site_dir)
```

## Testing

The sitemap generator includes unit tests that verify:

1. All expected pages are included in the sitemap
2. Priorities are correctly assigned based on page types
3. Change frequencies are correctly assigned based on page types
4. Custom configurations are properly applied

## Future Enhancements

Potential future enhancements to the sitemap generation process include:

1. **Image Sitemaps**: Adding support for image sitemaps to help search engines discover and index images
2. **Video Sitemaps**: Adding support for video sitemaps if video content is added to the site
3. **Sitemap Index**: Supporting sitemap indexes for larger sites with multiple sitemaps
4. **Dynamic Generation**: Adapting the generator for server-side rendering if the site moves away from static generation

## SSR Compatibility

The standalone approach to sitemap generation makes it easier to adapt to a potential future move to server-side rendering (SSR). In an SSR environment, the sitemap generator could be:

1. Run as a scheduled job to periodically regenerate the sitemap
2. Modified to work with a database or content API instead of scanning the file system
3. Triggered by content updates rather than builds

The core logic for generating the XML structure would remain largely unchanged, with only the page discovery mechanism needing significant changes.
