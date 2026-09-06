from django.db import models
from django.utils import timezone


class UssdSession(models.Model):
    class State(models.TextChoices):
        MENU = 'MENU', 'Main menu'
        REGISTER_NAME = 'REGISTER_NAME', 'Registration name'
        REGISTER_LOCATION = 'REGISTER_LOCATION', 'Registration location'
        REGISTER_EDUCATION = 'REGISTER_EDUCATION', 'Registration education'
        REGISTER_SKILLS = 'REGISTER_SKILLS', 'Registration skills'
        REGISTER_INTERESTS = 'REGISTER_INTERESTS', 'Registration interests'
        OPPORTUNITIES = 'OPPORTUNITIES', 'Opportunity list'
        OPPORTUNITY_DETAIL = 'OPPORTUNITY_DETAIL', 'Opportunity detail'
        OPPORTUNITY_APPLY = 'OPPORTUNITY_APPLY', 'Opportunity application'
        PROGRAMME = 'PROGRAMME', 'Programme menu'
        CHECKIN = 'CHECKIN', 'Monitoring check-in'
        CHECKIN_CHALLENGE = 'CHECKIN_CHALLENGE', 'Check-in challenge'
        CHECKIN_CATEGORY = 'CHECKIN_CATEGORY', 'Check-in challenge category'
        CHALLENGE = 'CHALLENGE', 'Challenge menu'
        PROFILE = 'PROFILE', 'Profile menu'
        PROFILE_LOCATION = 'PROFILE_LOCATION', 'Profile location'
        PROFILE_EDUCATION = 'PROFILE_EDUCATION', 'Profile education'
        PROFILE_SKILLS = 'PROFILE_SKILLS', 'Profile skills'
        PROFILE_INTERESTS = 'PROFILE_INTERESTS', 'Profile interests'

    session_id = models.CharField(max_length=120, unique=True, db_index=True)
    phone_number = models.CharField(max_length=30, db_index=True)
    service_code = models.CharField(max_length=30, blank=True)
    network_code = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=40, choices=State.choices, default=State.MENU)
    temporary_data = models.JSONField(default=dict, blank=True)
    completed = models.BooleanField(default=False)
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['phone_number', 'completed'])]

    def is_expired(self):
        return self.expires_at <= timezone.now()
