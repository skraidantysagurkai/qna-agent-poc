# qna-agent-poc
Python based QnA agent service

## Environment Setup
**Prerequisites:**
- Uv, can be installed from [here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

Create a conda environment using the provided `requirements.txt` file:

**Environment Creation:**
```bash
uv sync
```

**Configuration:**
Create a `.env` file in the root directory by renaming the provided `.env.example` file. Update the environment variables in the `.env` file with your specific configuration details.

## Running the Application
To start the application, run the following command:

```bash
uv run python main.py
```
This will start the FastAPI server at `http://0.0.0.0:8080`

## Running in docker
To start the application in a docker container, run the following command:
```bash
docker-compose up --build
```
Note that you need to have docker installed on your machine. For more information, see the [docker documentation](https://docs.docker.com/get-docker/).

## Running Tests
To run the tests, use the following command:

```bash
uv run python -m unittest discover tests
```

## API Endpoints

The application provides the following REST API endpoints:

### Chat Endpoint
**POST** `/chat/`

Processes natural language questions and returns AI-generated answers with sources.

**Input Format:**
```json
{
  "question": "How do I integrate proxies?"
}
```

**Output Format:**
```json
{
  "answer": "Some answer",
  "sources": [
    "url1",
    "url2"
  ]
}
```

**Exceptions:**
- `400 Bad Request`: Invalid question format or empty question
- `500 Internal Server Error`: LLM service unavailable or processing error

### Health Check Endpoint
**GET** `/health/`

Returns the service health status and version information.

**Input Format:** No input required

**Output Format:**
```json
{
  "status": "OK",
  "version": "0.1.0"
}
```

**Exceptions:**
- `500 Internal Server Error`: Service configuration error

**Base URL:** `http://0.0.0.0:8080` (when running locally)

## Custom Data Format

If you want to use a custom scraped data dataset, please make sure that it is in the format of:
```json
[
  {
    "url": "https://something.com/some-page",
    "content": "This is the text content of the page."
  }
]
```

## Tools:

### Scraper:

You can find the scraper used in this exercise in `tools/scraping/scraper.py`.

#### Description

This scraper fetches pages from a sitemap XML, parses the relevant text content from documentation pages, and stores the results as JSON. 
It is designed to work on small to medium documentation sites and currently runs on **a single thread**, which is sufficient for scraping tasks under 1,000 pages.

#### First Things First

Before you run the scraper on a website, ensure that you have permission to scrape the site. Check the website's `robots.txt` file and terms of service to confirm that web scraping is allowed. 
Always respect the website's rules and guidelines. For this and to find the websites sitemap, you can use the created tool in `tools/scraping/reading_robot.py`.
Launching it via CLI:

```bash
uv run python tools/scraping/reading_robot.py --base_url <website_url>
```

#### Usage

The scraper uses the following CLI arguments:

| Full Argument Name   | Short Argument Name | Description                                                          | Default Value | Type |
|----------------------|---------------------|----------------------------------------------------------------------|---------------|------|
| `--site_map_url`     | `-s`                | Site Map Url                                                         | - (required)  | str  |
| `--num_sections`     | `-n`                | Number of sections to scrape (filters by most numerous)              | 2             | int  |
| `--output_file_name` | `-o`                | Output JSON file name, data will be stored in data folder            | raw_data.json | str  |
| `--batch_size`       | `-b`                | Size of batch to save data incrementally (not to lose data on crash) | 100           | int  |

And can be run via CLI like this:

```bash
uv run python tools/scraping/scraper.py --site_map_url <sitemap_url> --num_sections 2 --output_file_name raw_data.json --batch_size 100
```

The data will be saved in chunks (of size defined by `--batch_size`) to the `data/` folder.
`