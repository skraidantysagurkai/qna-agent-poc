# qna-agent-poc
Python based QnA agent service


# Tools:

## Scraper:

You can find the scraper used in this exercise in `tools/scraping/scraper.py`.

### Description

This scraper fetches pages from a sitemap XML, parses the relevant text content from documentation pages, and stores the results as JSON. 
It is designed to work on small to medium documentation sites and currently runs on **a single thread**, which is sufficient for scraping tasks under 1,000 pages.

### First Things First

Before you run the scraper on a website, ensure that you have permission to scrape the site. Check the website's `robots.txt` file and terms of service to confirm that web scraping is allowed. 
Always respect the website's rules and guidelines. For this and to find the websites sitemap, you can use the created tool in `tools/scraping/reading_robot.py`.
Launching it via CLI:

```bash
python tools/scraping/reading_robot.py --base_url <website_url>
```

### Usage

The scraper uses the following CLI arguments:

| Full Argument Name   | Short Argument Name | Description                                                          | Default Value | Type |
|----------------------|---------------------|----------------------------------------------------------------------|---------------|------|
| `--site_map_url`     | `-s`                | Site Map Url                                                         | - (required)  | str  |
| `--num_sections`     | `-n`                | Number of sections to scrape (filters by most numerous)              | 2             | int  |
| `--output_file_name` | `-o`                | Output JSON file name, data will be stored in data folder            | raw_data.json | str  |
| `--batch_size`       | `-b`                | Size of batch to save data incrementally (not to lose data on crash) | 100           | int  |

And can be run via CLI like this:

```bash
python tools/scraping/scraper.py --site_map_url <sitemap_url> --num_sections 2 --output_file_name raw_data.json --batch_size 100
```

The data will be saved in chunks (of size defined by `--batch_size`) to the `data/` folder.