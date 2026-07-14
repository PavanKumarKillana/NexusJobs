import os
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from jobs.models import JobCategory, JobPosting

def scrape_realtime_jobs():
    print("Fetching real-time remote jobs from API...")
    url = "https://remotive.com/api/remote-jobs?limit=10"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch from API: {e}")
        return

    jobs = data.get('jobs', [])
    if not jobs:
        print("No jobs found in API response.")
        return

    # Get or create categories
    pvt_cat, _ = JobCategory.objects.get_or_create(name='Private Jobs', slug='private')
    gov_cat, _ = JobCategory.objects.get_or_create(name='Government Jobs', slug='government')
    
    count = 0
    for job_data in jobs:
        try:
            title = job_data.get('title', 'Unknown Title')
            company = job_data.get('company_name', 'Unknown Company')
            link = job_data.get('url', '')
            location = job_data.get('candidate_required_location', 'Remote')
            
            # The API returns the description in HTML, so we strip it to clean text
            html_desc = job_data.get('description', '')
            clean_desc = BeautifulSoup(html_desc, 'html.parser').get_text(separator='\n\n')
            
            # Limit the description size to avoid massive database entries if needed
            if len(clean_desc) > 5000:
                clean_desc = clean_desc[:5000] + "...\n(Read more on the website)"

            # We'll randomly assign Government to some just to populate categories, or default to private
            # In reality, Remotive is mostly Private tech jobs.
            cat = pvt_cat
            if 'gov' in title.lower() or 'federal' in title.lower():
                cat = gov_cat

            # Check if job already exists
            import random
            if not JobPosting.objects.filter(title=title, company_name=company).exists():
                JobPosting.objects.create(
                    title=title,
                    company_name=company,
                    location=location,
                    category=cat,
                    description=clean_desc,
                    apply_link=link,
                    vacancies=random.randint(1, 7)
                )
                count += 1
                print(f"Added Real-Time Job: {title} at {company}")
        except Exception as e:
            print(f"Error processing job {title}: {e}")
            
    print(f"Scraping complete. {count} new real-time jobs added.")

if __name__ == '__main__':
    scrape_realtime_jobs()
