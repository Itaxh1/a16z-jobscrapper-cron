

# A16z Software Engineering Jobs Dashboard

### Overview

This project consists of two components:

1. **A16zJobsScraper** — a Python-based Selenium + BeautifulSoup scraper that extracts **Software Engineering jobs** from [a16z.com/jobs](https://jobs.a16z.com).
2. **Flask + Tailwind Dashboard** — a lightweight, interactive web dashboard for visualizing the scraped data with filters, statistics, and live refresh capability.

Together, they form a complete pipeline for collecting, storing, and exploring SDE job opportunities across A16z portfolio companies.



## Features

### Scraper

* Scrapes all A16z portfolio companies and their job listings.
* Filters automatically for **SDE-related** roles (`software`, `engineer`, `developer`, `backend`, `frontend`, etc.).
* Saves jobs to both **JSON** and **CSV** formats.
* Handles **headless browsing** via ChromeDriver.
* Automatically normalizes URLs and cleans job data.
* Interactive filters:
* Search by job title or company
* Filter by company or location
* Clear filters and refresh live data
* 
* RESTful API:
  * `/api/jobs` → returns all jobs in JSON
  * `/api/stats` → returns summary statistics



## Project Structure

```
📁 a16z-jobs-dashboard/
├── app.py                     # Flask dashboard
├── scraper.py                 # Selenium + BeautifulSoup scraper
├── a16z_sde_jobs.json         # Scraped jobs (auto-generated)
├── a16z_sde_jobs.csv          # Optional CSV export (auto-generated)
├── requirements.txt           # Python dependencies
└── README.md                  # Documentation (this file)
```



## Tech Stack

| Layer              | Technology               |
| ------------------ | ------------------------ |
| **Frontend**       | Tailwind CSS, Vanilla JS |
| **Backend**        | Flask (Python)           |
| **Data Storage**   | JSON / CSV               |
| **Scraping**       | Selenium + BeautifulSoup |
| **Browser Driver** | Headless Chrome          |



##  API Endpoints

| Endpoint     | Description            | Method | Example Output                              |
| ------------ | ---------------------- | ------ | ------------------------------------------- |
| `/`          | Main Dashboard         | `GET`  | HTML Page                                   |
| `/api/jobs`  | Fetch all job listings | `GET`  | `[{"company": "...", "title": "..."}]`      |
| `/api/stats` | Summary statistics     | `GET`  | `{"total_jobs": 32, "total_companies": 10}` |


##  How It Works

1. **Scraper (scraper.py)**

   * Loads all companies from `https://jobs.a16z.com/companies`.
   * Visits each company’s job page.
   * Extracts relevant details (`title`, `company`, `location`, `url`).
   * Filters to include only Software Engineering roles.
   * Saves results to local JSON/CSV files.

2. **Dashboard (app.py)**

   * Loads job data from `a16z_sde_jobs.json`.
   * Calculates statistics dynamically.
   * Serves an interactive UI via TailwindCSS.
   * Supports API calls for dynamic refresh.


##  Example Job Record

```json
{
  "company": "OpenAI",
  "title": "Software Engineer - Backend",
  "location": "San Francisco, CA",
  "url": "https://jobs.a16z.com/job/openai/backend-engineer",
  "scraped_from": "https://jobs.a16z.com/jobs/openai"
}
```


## Troubleshooting

* **ChromeDriver Issues:**
  Ensure Chrome and `chromedriver` versions are compatible.
  You can install ChromeDriver via:

  ```bash
  sudo apt install chromium-chromedriver
  ```

* **Empty Results:**
  If no jobs are found, the website structure might have changed.
  Update the selectors in `scrape_company_jobs()`.

* **Dashboard Not Loading:**
  Make sure `a16z_sde_jobs.json` exists and is valid JSON.


##  Future Improvements

* Integrate database (e.g., SQLite, MongoDB) for persistent storage
* Add pagination & job detail pages
* Deploy Flask app via Docker or Cloud Run
* Schedule scraper to auto-refresh daily
