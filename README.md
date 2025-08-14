# Confluence Page Date Analysis Tool

A Python script that analyzes Confluence pages to extract modification and view dates, outputting results to CSV format with sorting and progress tracking.

## Features

- **Page Analysis**: Extract last modified and/or last viewed dates for all pages in a Confluence space
- **CSV Export**: Generate sorted CSV reports with page titles, URLs, and dates
- **Progress Tracking**: Real-time progress updates during page fetching and analysis
- **Flexible Configuration**: Use environment files or manual input for credentials
- **Command Line Interface**: Easy-to-use CLI with multiple output options

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/sladehouseltd/confluence_api.git
   cd confluence_api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Option 1: Environment File (Recommended)

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Confluence credentials:
   ```bash
   CONFLUENCE_URL=https://yourcompany.atlassian.net/wiki
   CONFLUENCE_USERNAME=your.email@company.com
   CONFLUENCE_PASSWORD=your_api_token_or_password
   ```

### Option 2: Manual Input

If no `.env` file is found, the script will prompt you to enter your credentials manually.

## Usage

### Basic Commands

```bash
# Get modification dates for all pages in a space
python confluence_page_dates.py SPACE_KEY --date-modified

# Get view dates for all pages in a space
python confluence_page_dates.py SPACE_KEY --date-viewed

# Get both modification and view dates
python confluence_page_dates.py SPACE_KEY --date-modified --date-viewed

# Specify custom output filename
python confluence_page_dates.py SPACE_KEY --date-modified --output my_report.csv
```

### Command Line Options

- `space`: **Required** - The Confluence space key to analyze
- `--date-modified`: Include last modified dates in the output
- `--date-viewed`: Include last viewed dates in the output
- `--output`, `-o`: Specify custom output CSV filename (default: auto-generated with timestamp)

**Note**: You must specify at least one of `--date-modified` or `--date-viewed`.

## Output Format

The generated CSV will contain the following columns based on your options:

### Modified Dates Only (`--date-modified`)
| page | page_url | date_modified |
|------|----------|---------------|
| Page Title | https://company.atlassian.net/wiki/display/SPACE/123456 | 2024-08-14 10:30:15 |

### View Dates Only (`--date-viewed`)
| page | page_url | date_viewed |
|------|----------|-------------|
| Page Title | https://company.atlassian.net/wiki/display/SPACE/123456 | 2024-08-13 14:22:10 |

### Both Dates (`--date-modified --date-viewed`)
| page | page_url | date_modified | date_viewed |
|------|----------|---------------|-------------|
| Page Title | https://company.atlassian.net/wiki/display/SPACE/123456 | 2024-08-14 10:30:15 | 2024-08-13 14:22:10 |

**Sorting**: Results are automatically sorted by date in descending order (most recent first).

## Progress Tracking

The script provides real-time progress updates:

```
Fetching pages from Confluence...
Fetched 50 pages so far...
Fetched 100 pages so far...
Found 150 pages to analyze...
Analyzed 50/150 pages...
Analyzed 100/150 pages...
Analysis complete - processed 150 pages
Results written to confluence_pages_SPACE_20240814_143022.csv
Analysis complete. Found 150 pages.
```

## Authentication

### Confluence Cloud
Use your email and an API token (recommended):
- Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens
- Use your email as the username
- Use the API token as the password

### Confluence Server/Data Center
Use your regular username and password.

## Error Handling

- **Invalid credentials**: The script will display authentication errors
- **Non-existent space**: Returns empty results if the space doesn't exist
- **Network issues**: Displays connection errors with retry suggestions
- **Missing data**: Pages without modification/view data show 'N/A' in the CSV

## Examples

```bash
# Analyze the DEV space for modification dates
python confluence_page_dates.py DEV --date-modified

# Get comprehensive report for DOCS space
python confluence_page_dates.py DOCS --date-modified --date-viewed --output docs_analysis.csv

# Quick view analysis for MARKETING space
python confluence_page_dates.py MARKETING --date-viewed
```

## Requirements

- Python 3.7+
- requests >= 2.25.0
- Valid Confluence account with space access permissions

## Troubleshooting

### Common Issues

1. **403 Permission Denied**: Check your credentials and ensure you have access to the specified space
2. **Connection Timeout**: Verify your Confluence URL is correct and accessible
3. **Empty Results**: Confirm the space key exists and contains pages
4. **View Data Shows "N/A"**: Page view analytics are often not available through the REST API. This is a limitation of most Confluence instances where analytics are either disabled, not accessible via API, or require special permissions. The `--date-modified` option will work reliably, but `--date-viewed` may return "N/A" for all pages.

### Getting Help

If you encounter issues:
1. Verify your Confluence URL format (should end with `/wiki` for Cloud)
2. Test your credentials by logging into Confluence manually
3. Ensure the space key is correct (case-sensitive)
4. Check that you have appropriate permissions for the space

## License

This project is part of the Sladehouse Ltd tooling suite for Atlassian integrations.