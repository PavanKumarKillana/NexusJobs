from django.db import models

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Job Categories"

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField(help_text="Detailed Job Description (JD)")
    vacancies = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    apply_link = models.URLField(max_length=500, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} at {self.company_name or 'N/A'}"
