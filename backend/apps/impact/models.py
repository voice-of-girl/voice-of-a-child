from django.db import models
from django.conf import settings
from apps.programmes.models import Programme

class KPI(models.Model):
    class Category(models.TextChoices):
        INPUT = 'INPUT', 'Input (Resources, Budget, Equipment)'
        ACTIVITY = 'ACTIVITY', 'Activity (Trainings, Workshops, Mentorship Sessions)'
        OUTPUT = 'OUTPUT', 'Output (Participants Reached, Trained, Completed)'
        OUTCOME = 'OUTCOME', 'Outcome (Employment, Skills Acquired, Income Gained)'
        IMPACT = 'IMPACT', 'Longer-term Impact (Sustained Business, Career Trajectory)'

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='kpis'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OUTPUT)
    target_value = models.FloatField()
    current_value = models.FloatField(default=0.0)
    unit = models.CharField(max_length=50, default='participants') # e.g. participants, USD, hours, %
    measurement_frequency = models.CharField(max_length=50, default='Monthly') # e.g. Weekly, Monthly, Milestone

    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0.0
        return min(100.0, round((self.current_value / self.target_value) * 100, 1))

    def __str__(self):
        return f"KPI: {self.name} ({self.current_value}/{self.target_value} {self.unit})"

class OutcomeMeasurement(models.Model):
    class Stage(models.TextChoices):
        BASELINE = 'BASELINE', 'Baseline (Before Programme)'
        MIDLINE = 'MIDLINE', 'Midline / Monitoring'
        ENDLINE = 'ENDLINE', 'Endline (Immediately After)'
        FOLLOW_UP_3M = 'FOLLOW_UP_3M', 'Follow-up (3 Months)'
        FOLLOW_UP_6M = 'FOLLOW_UP_6M', 'Follow-up (6 Months)'
        FOLLOW_UP_12M = 'FOLLOW_UP_12M', 'Follow-up (12 Months)'

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='outcome_measurements'
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='outcome_records'
    )
    stage = models.CharField(max_length=30, choices=Stage.choices)
    
    # Tracked dimensions
    employment_status = models.CharField(max_length=100, blank=True)
    education_status = models.CharField(max_length=100, blank=True)
    skills_level = models.CharField(max_length=100, blank=True) # Beginner, Intermediate, Advanced
    monthly_income_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    business_established = models.BooleanField(default=False)
    confidence_score = models.IntegerField(default=5, help_text="Rating 1-10")
    
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('programme', 'beneficiary', 'stage')

    def __str__(self):
        return f"{self.beneficiary.email} [{self.stage}] in {self.programme.title}"
