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

            # Try to extract real vacancy count
            import re
            vacancies = 1
            vac_match = re.search(r'(\d+)\s*(?:vacancies|posts|vacancy|post)', title + ' ' + clean_desc, re.IGNORECASE)
            if vac_match:
                vacancies = int(vac_match.group(1))

            # Check if job already exists
            if not JobPosting.objects.filter(title=title, company_name=company).exists():
                JobPosting.objects.create(
                    title=title,
                    company_name=company,
                    location=location,
                    category=cat,
                    description=clean_desc,
                    apply_link=link,
                    vacancies=vacancies
                )
                count += 1
                print(f"Added Real-Time Job: {title} at {company}")
        except Exception as e:
            print(f"Error processing job {title}: {e}")
            
    print(f"Scraping complete. {count} new real-time jobs added.")

def scrape_youth_government_jobs():
    print("Fetching REAL Government & Youth jobs from news/rss portals...")
    gov_cat, _ = JobCategory.objects.get_or_create(name='Government Jobs', slug='government')
    
    import random
    import xml.etree.ElementTree as ET
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Use FreeJobAlert RSS which tracks SSC, UPSC, State Govt, etc.
    url = "https://www.freejobalert.com/feed/"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except Exception as e:
        print(f"Failed to fetch govt RSS feed: {e}")
        return
        
    count = 0
    # Clean up existing bad data (like proverbs) that might have leaked in
    bad_keywords = ['proverb', 'quote', 'current affairs', 'gk', 'meaning', 'lesson', 'motivation']
    for bad in bad_keywords:
        JobPosting.objects.filter(title__icontains=bad).delete()

    # Find all items in the RSS feed
    for item in root.findall('.//item')[:25]:  # Check more items since we are filtering
        try:
            title = item.find('title').text
            lower_title = title.lower()
            
            # 1. Skip non-job posts
            if any(bad in lower_title for bad in bad_keywords):
                continue
                
            # 2. Require job-related keywords
            valid_keywords = ['admit card', 'result', 'exam', 'recruitment', 'posts', 'vacancies', 'syllabus', 'answer key', 'notification', 'online form', 'call letter', 'job', 'psc', 'ssc', 'upsc', 'board']
            if not any(valid in lower_title for valid in valid_keywords):
                continue

            link = item.find('link').text
            description_html = item.find('description').text
            
            # Clean HTML out of description
            clean_desc = BeautifulSoup(description_html, 'html.parser').get_text(separator=' ')
            
            import re
            official_link = link
            # Extract .gov.in or .nic.in domain if present in text
            gov_match = re.search(r'([a-zA-Z0-9.-]+\.(?:gov\.in|nic\.in))', clean_desc, re.IGNORECASE)
            if gov_match:
                official_link = "https://" + gov_match.group(1).lower()
            
            # Extract actual vacancies using regex
            vacancies = 1
            vac_match = re.search(r'(\d+)\s*(?:vacancies|posts|vacancy|post)', title + ' ' + clean_desc, re.IGNORECASE)
            if vac_match:
                vacancies = int(vac_match.group(1))
                
            if not JobPosting.objects.filter(title=title).exists():
                JobPosting.objects.create(
                    title=title,
                    company_name="Government of India / State Govt",
                    location="India",
                    category=gov_cat,
                    description=clean_desc,
                    apply_link=official_link,
                    vacancies=vacancies
                )
                count += 1
                print(f"Added Govt Job: {title}")
        except Exception as e:
            continue
            
    print(f"Real Youth/Govt jobs complete. {count} added.")

if __name__ == '__main__':
    scrape_realtime_jobs()
    scrape_youth_government_jobs()

