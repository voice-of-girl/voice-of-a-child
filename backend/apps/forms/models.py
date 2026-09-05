from django.db import models
from django.conf import settings
from apps.organisations.models import Organisation
from apps.programmes.models import Programme

class Form(models.Model):
    class FormType(models.TextChoices):
        BASELINE = 'BASELINE', 'Baseline Form'
        MONITORING = 'MONITORING', 'Monitoring Form'
        ENDLINE = 'ENDLINE', 'Endline Form'
        FOLLOW_UP = 'FOLLOW_UP', 'Follow-up Form'
        CUSTOM = 'CUSTOM', 'Custom Survey'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'
        CLOSED = 'CLOSED', 'Closed'

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='forms'
    )
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name='forms'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=30, choices=FormType.choices, default=FormType.BASELINE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    response_deadline = models.DateTimeField(null=True, blank=True)
    follow_up_interval_months = models.IntegerField(null=True, blank=True, help_text="e.g. 3, 6, or 12 months")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} [{self.get_form_type_display()}]"

class FormQuestion(models.Model):
    class QuestionType(models.TextChoices):
        SHORT_TEXT = 'SHORT_TEXT', 'Short Text'
        LONG_TEXT = 'LONG_TEXT', 'Long Text / Paragraph'
        NUMBER = 'NUMBER', 'Number'
        MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple Choice (Single Select)'
        CHECKBOX = 'CHECKBOX', 'Checkboxes (Multi Select)'
        DROPDOWN = 'DROPDOWN', 'Dropdown'
        YES_NO = 'YES_NO', 'Yes / No'
        RATING_SCALE = 'RATING_SCALE', 'Rating Scale (1-5 or 1-10)'
        DATE = 'DATE', 'Date'
        FILE_UPLOAD = 'FILE_UPLOAD', 'File Upload'

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.CharField(max_length=500)
    help_text = models.CharField(max_length=255, blank=True)
    question_type = models.CharField(max_length=30, choices=QuestionType.choices)
    required = models.BooleanField(default=True)
    options = models.JSONField(default=list, blank=True, help_text="Array of string choices for choice/checkbox/dropdown/rating")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text}"

class FormResponse(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        SUBMITTED = 'SUBMITTED', 'Submitted'

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='form_responses'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    submitted_via = models.CharField(max_length=50, default='WEB', help_text="WEB, FIELD_OFFICER, SMS, WHATSAPP")
    assisted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assisted_responses',
        help_text="Field officer who assisted during field visit"
    )

    class Meta:
        unique_together = ('form', 'beneficiary')

    def __str__(self):
        return f"{self.form.title} - {self.beneficiary.email} ({self.status})"

class FormAnswer(models.Model):
    response = models.ForeignKey(
        FormResponse,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        FormQuestion,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    value = models.JSONField(help_text="Can be string, number, array of selected strings, or boolean")

    class Meta:
        unique_together = ('response', 'question')

    def __str__(self):
        return f"Ans to {self.question_id}: {self.value}"
