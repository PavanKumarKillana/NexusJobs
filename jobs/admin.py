from django.contrib import admin
from .models import JobCategory, JobPosting

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'company_name', 'vacancies', 'location', 'posted_at', 'is_active')
    list_filter = ('category', 'is_active', 'posted_at')
    search_fields = ('title', 'company_name', 'location', 'description')
