import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from jobs.models import JobCategory, JobPosting

def seed():
    # Create categories
    gov, _ = JobCategory.objects.get_or_create(name='Government Jobs', slug='government')
    pvt, _ = JobCategory.objects.get_or_create(name='Private Jobs', slug='private')
    std, _ = JobCategory.objects.get_or_create(name='Student Internships', slug='student')

    # Create dummy jobs
    JobPosting.objects.get_or_create(
        title='Software Engineer Trainee',
        category=std,
        description='We are looking for an enthusiastic software engineer trainee to join our fast-growing startup. You will work on cutting-edge AI technologies and help build scalable backend systems.',
        vacancies=5,
        location='Remote',
        company_name='TechNova Solutions',
        apply_link='https://example.com/apply'
    )

    JobPosting.objects.get_or_create(
        title='Senior Data Scientist',
        category=pvt,
        description='Join our core analytics team to drive data-driven decision making. You should have 5+ years of experience in Python, SQL, and machine learning algorithms.',
        vacancies=2,
        location='Bangalore, India',
        company_name='DataCorp AI',
        apply_link='https://example.com/apply-data'
    )

    JobPosting.objects.get_or_create(
        title='Railway Accounts Officer',
        category=gov,
        description='Official notification for the post of Railway Accounts Officer. Candidates must have a degree in Commerce and clear the departmental examination. Great benefits and job security.',
        vacancies=120,
        location='New Delhi, India',
        company_name='Indian Railways',
        apply_link='https://example.com/gov'
    )
    
    print("Dummy data seeded successfully!")

if __name__ == '__main__':
    seed()
