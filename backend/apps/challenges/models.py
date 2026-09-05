from django.db import models
from django.conf import settings
from apps.programmes.models import Programme

class Challenge(models.Model):
    class Category(models.TextChoices):
        TRANSPORT = 'TRANSPORT', 'Transportation Issues'
        FINANCIAL = 'FINANCIAL', 'Financial & Upkeep'
        HEALTH = 'HEALTH', 'Health & Wellbeing'
        ATTENDANCE = 'ATTENDANCE', 'Attendance Difficulty'
        SAFETY = 'SAFETY', 'Safety & Protection'
        MATERIALS = 'MATERIALS', 'Lack of Materials / Equipment'
        FAMILY_CARE = 'FAMILY_CARE', 'Family & Childcare Duties'
        OTHER = 'OTHER', 'Other Challenge'

    class Severity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical / Urgent'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'

    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='challenges'
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_challenges'
    )
    category = models.CharField(max_length=30, choices=Category.choices)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_challenges'
    )
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    action_plan = models.TextField(blank=True)
    
    audit_history = models.JSONField(default=list, blank=True)

    def log_history(self, actor_email, action, note=""):
        from django.utils import timezone
        record = {
            'timestamp': timezone.now().isoformat(),
            'actor': actor_email,
            'action': action,
            'note': note
        }
        self.audit_history.append(record)

    def __str__(self):
        return f"[{self.severity}] {self.get_category_display()} - {self.programme.title} ({self.status})"
