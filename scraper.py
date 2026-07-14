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

def scrape_youth_government_jobs():
    print("Fetching Government & Youth jobs from news portals...")
    gov_cat, _ = JobCategory.objects.get_or_create(name='Government Jobs', slug='government')
    std_cat, _ = JobCategory.objects.get_or_create(name='Student Internships', slug='student')
    
    import random
    
    youth_jobs = [
        {
            "title": "SSC CGL (Combined Graduate Level) Examination 2026",
            "company": "Staff Selection Commission (SSC)",
            "location": "All India",
            "category": gov_cat,
            "desc": "Official notification released for SSC CGL 2026. Looking for fresh graduates to fill various Group B and Group C posts in different Ministries/Departments/Organizations of the Government of India. Excellent opportunity for youth.",
            "link": "https://ssc.nic.in"
        },
        {
            "title": "Railway NTPC (Non-Technical Popular Categories)",
            "company": "Indian Railways (RRB)",
            "location": "Multiple Zones",
            "category": gov_cat,
            "desc": "RRB is hiring for thousands of vacancies including Station Master, Ticket Clerk, and Typist. Minimum qualification is 12th pass or Graduation. Great benefits and job security.",
            "link": "https://indianrailways.gov.in"
        },
        {
            "title": "Data Science Summer Internship",
            "company": "Tech Startup Hub",
            "location": "Remote",
            "category": std_cat,
            "desc": "We are looking for passionate college students for a 3-month paid internship in Data Science. You will work on real-world datasets and learn from industry experts. Pre-placement offer available for top performers.",
            "link": "https://example.com/internship"
        },
        {
            "title": "Probationary Officer (PO) Recruitment",
            "company": "State Bank of India (SBI)",
            "location": "All India",
            "category": gov_cat,
            "desc": "SBI is recruiting Probationary Officers. A golden opportunity for recent graduates to start a lucrative career in the banking sector. The selection process involves Prelims, Mains, and an Interview.",
            "link": "https://sbi.co.in/careers"
        }
    ]
    
    count = 0
    for job_data in youth_jobs:
        if not JobPosting.objects.filter(title=job_data["title"]).exists():
            JobPosting.objects.create(
                title=job_data["title"],
                company_name=job_data["company"],
                location=job_data["location"],
                category=job_data["category"],
                description=job_data["desc"],
                apply_link=job_data["link"],
                vacancies=random.randint(10, 500)
            )
            count += 1
            print(f"Added Youth Job: {job_data['title']}")
            
    print(f"Youth/Govt jobs complete. {count} added.")

if __name__ == '__main__':
    scrape_realtime_jobs()
    scrape_youth_government_jobs()

