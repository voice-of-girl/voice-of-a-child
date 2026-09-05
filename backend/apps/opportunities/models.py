from django.db import models
from apps.programmes.models import Programme

class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        SCHOLARSHIP = 'SCHOLARSHIP', 'Scholarship'
        JOB = 'JOB', 'Job Placement'
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        TRAINING = 'TRAINING', 'Skills Training'
        MENTORSHIP = 'MENTORSHIP', 'Mentorship'
        FELLOWSHIP = 'FELLOWSHIP', 'Fellowship'
        ENTREPRENEURSHIP = 'ENTREPRENEURSHIP', 'Entrepreneurship Seed Fund'
        GRANT = 'GRANT', 'Grant'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open for Applications'
        CLOSED = 'CLOSED', 'Closed'
        FILLED = 'FILLED', 'Filled'

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='opportunities'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    opportunity_type = models.CharField(max_length=30, choices=OpportunityType.choices)
    benefits = models.TextField(help_text="Stipend, laptop, mentorship, certification, etc.")
    requirements = models.TextField()
    application_deadline = models.DateField()
    available_slots = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.get_opportunity_type_display()})"
