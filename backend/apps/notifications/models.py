from django.db import models
from django.conf import settings

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        OPPORTUNITY = 'OPPORTUNITY', 'New Opportunity'
        FORM_ASSIGNED = 'FORM_ASSIGNED', 'Form / Survey Assigned'
        FORM_DEADLINE = 'FORM_DEADLINE', 'Form Deadline Reminder'
        APPLICATION_STATUS = 'APPLICATION_STATUS', 'Application Status Update'
        CHALLENGE_UPDATE = 'CHALLENGE_UPDATE', 'Challenge Resolution Update'
        FOLLOW_UP_SURVEY = 'FOLLOW_UP_SURVEY', 'Long-term Follow-up Survey'
        SYSTEM = 'SYSTEM', 'System Alert'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    action_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient.email}: {self.title}"
