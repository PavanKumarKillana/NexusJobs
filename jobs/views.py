from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import JobPosting, JobCategory

def job_list(request):
    jobs = JobPosting.objects.filter(is_active=True).select_related('category')
    categories = JobCategory.objects.all()
    
    # Highlights: Jobs posted in the last 24 hours (or just top 5 latest for demo)
    twenty_four_hours_ago = timezone.now() - timedelta(days=1)
    highlights = JobPosting.objects.filter(is_active=True, posted_at__gte=twenty_four_hours_ago).order_by('-posted_at')[:5]
    
    # Fallback for highlights if database is just seeded
    if not highlights.exists():
        highlights = JobPosting.objects.filter(is_active=True).order_by('-posted_at')[:5]
    
    category_slug = request.GET.get('category')
    if category_slug:
        jobs = jobs.filter(category__slug=category_slug)
        
    context = {
        'jobs': jobs,
        'categories': categories,
        'selected_category': category_slug,
        'highlights': highlights
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    job = get_object_or_404(JobPosting, pk=pk, is_active=True)
    return render(request, 'jobs/job_detail.html', {'job': job})

from django.http import JsonResponse
import os
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def ai_summarize_job(request, pk):
    job = get_object_or_404(JobPosting, pk=pk, is_active=True)
    
    # Simple Mock/Fallback for demo purposes if API key is not set
    mock_summary = f"🚀 {job.title} at {job.company_name} is an excellent opportunity.\n📌 Location: {job.location}\n💼 They are looking for someone with skills related to the job description."
    
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if HAS_GENAI and api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Summarize this job description in 3 bullet points for a quick read:\nTitle: {job.title}\nCompany: {job.company_name}\nDescription: {job.description}"
            response = model.generate_content(prompt)
            return JsonResponse({'summary': response.text})
        except Exception as e:
            return JsonResponse({'summary': mock_summary, 'error': str(e)})
            
    return JsonResponse({'summary': mock_summary})

