# Subscribe Page

The subscribe page provides subscription options for users to access different tiers of content on the Rat News Network.

## Overview

The subscribe page presents three subscription tiers:
- Basic Rat (Free)
- Premium Rat (🧀¢9.99/mo)
- Big Cheese (🧀¢29.99/mo)

## Implementation

The subscribe page is implemented as a static HTML page using the site's Jinja2 templating system. The page extends the base template and is generated during the site build process by the `generate_subscribe_page()` method in the `ArticleSiteGenerator` class.

## Template Structure

- `subscribe.html` - The main template that defines the subscription packages
- Extends `base.html` for consistent site layout and styling
- Uses existing CSS classes defined in `styles.css` for styling the subscription packages

## Integration

The subscribe page is accessible via the "Subscribe" button in the site header. The page is generated as part of the standard site generation process alongside other static pages like the article pages and QR code page.
