import os
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from jobs.models import JobCategory, JobPosting

def scrape_python_jobs():
    print("Scraping Python.org Jobs...")
    url = "https://www.python.org/jobs/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to retrieve jobs")
        return
        
    soup = BeautifulSoup(response.content, 'html.parser')
    job_list_elements = soup.find('ol', class_='list-recent-jobs')
    
    if not job_list_elements:
        print("Could not find job listings on page.")
        return
        
    jobs = job_list_elements.find_all('li')
    
    # Get or create the Private Jobs category
    pvt_cat, _ = JobCategory.objects.get_or_create(name='Private Jobs', slug='private')
    
    count = 0
    for job in jobs[:5]:  # Scrape first 5 jobs
        try:
            title_element = job.find('h2', class_='listing-company').find('a')
            company_element = job.find('h2', class_='listing-company').text.split('\n')
            
            title = title_element.text.strip()
            link = "https://www.python.org" + title_element['href']
            
            # The company name is usually the last part of the split text after stripping spaces
            company = company_element[-2].strip() if len(company_element) > 1 else "Unknown Company"
            
            location_element = job.find('span', class_='listing-location')
            location = location_element.text.strip() if location_element else "Remote"
            
            # Extract basic info since python.org job listings on the main page don't have full descriptions
            description = f"Scraped from python.org. Check out the link to apply for the {title} position at {company}."
            
            # Check if job already exists
            if not JobPosting.objects.filter(title=title, company_name=company).exists():
                JobPosting.objects.create(
                    title=title,
                    company_name=company,
                    location=location,
                    category=pvt_cat,
                    description=description,
                    apply_link=link,
                    vacancies=1
                )
                count += 1
                print(f"Added Job: {title} at {company}")
        except Exception as e:
            print(f"Error scraping a job: {e}")
            
    print(f"Scraping complete. {count} new jobs added.")

if __name__ == '__main__':
    scrape_python_jobs()
