# App Configuration

This file contains the configuration for the AI Trading Lab application. You can modify these values to customize the app without changing the main code.

## Configuration Options

- `app_name`: The full name of the application (used in page title and about menu)
- `app_display_name`: The display name shown in the app header (with emoji)
- `version`: The current version number
- `description`: Description shown in the about menu
- `tagline`: The tagline displayed under the app title
- `icon`: The emoji icon used for the app
- `copyright_year`: The year shown in the footer copyright

## How to Change App Information

1. Edit the `app_config.json` file
2. Modify any of the values above
3. Save the file
4. Restart the Streamlit app

The changes will be reflected immediately without modifying any Python code.

## Example Customizations

```json
{
  "app_name": "My Custom Trading App",
  "app_display_name": "My Trading Platform",
  "version": "1.0.0",
  "description": "Custom trading analysis platform",
  "tagline": "📊 Trade Smart • 🤖 AI Insights • 💰 Profit",
  "icon": "📈",
  "copyright_year": "2026"
}
```