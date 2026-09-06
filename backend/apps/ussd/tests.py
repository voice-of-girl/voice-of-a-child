from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.applications.models import Application
from apps.beneficiaries.models import BeneficiaryProfile
from apps.challenges.models import Challenge
from apps.forms.models import Form, FormQuestion, FormResponse
from apps.opportunities.models import Opportunity
from apps.organisations.models import Organisation
from apps.participation.models import BeneficiaryParticipation
from apps.programmes.models import Programme

from .models import UssdSession
from .services import UssdService
from .views import ussd_callback


@override_settings(ROOT_URLCONF='apps.ussd.test_urls')
class UssdServiceTests(TestCase):
    phone = '+256700000000'

    def setUp(self):
        self.organisation = Organisation.objects.create(
            name='Test Foundation', email='test@example.org', district='Kampala'
        )
        self.programme = Programme.objects.create(
            organisation=self.organisation,
            title='Digital Skills Programme',
            description='A skills programme',
            category='SKILLS',
            location='Kampala',
            start_date='2026-01-01',
            end_date='2026-12-31',
            status=Programme.Status.ACTIVE,
        )
        self.opportunity = Opportunity.objects.create(
            programme=self.programme,
            title='Digital Skills Scholarship',
            description='Learn digital skills',
            opportunity_type=Opportunity.OpportunityType.TRAINING,
            benefits='Training and mentorship',
            requirements='Interest in technology',
            application_deadline='2026-12-31',
            status=Opportunity.Status.OPEN,
        )

    def service(self, session='test-session'):
        return UssdService(session, self.phone, '*123#', 'network')

    def register(self):
        service = self.service('registration')
        service.handle('')
        service.handle('1')
        service.handle('Jane Doe')
        service.handle('Kampala')
        service.handle('4')
        service.handle('Python, Design')
        return service.handle('Technology, Leadership')

    def test_initial_request_returns_main_menu(self):
        response = self.service().handle('')
        self.assertTrue(response.startswith('CON '))
        self.assertIn('1. Register', response)
        self.assertIn('3. Opportunities', response)

    def test_registration_creates_one_phone_identified_participant(self):
        response = self.register()
        self.assertTrue(response.startswith('END '))
        self.assertEqual(CustomUser.objects.filter(phone_number=self.phone).count(), 1)
        self.assertEqual(BeneficiaryProfile.objects.get(user__phone_number=self.phone).district, 'Kampala')

        self.register()
        self.assertEqual(CustomUser.objects.filter(phone_number=self.phone).count(), 1)

    def test_existing_participant_lookup(self):
        user = CustomUser.objects.create_user(
            email='existing@example.org', first_name='Existing', last_name='Participant',
            phone_number=self.phone, role=CustomUser.Role.BENEFICIARY,
        )
        response = self.service().handle('2')
        self.assertTrue(response.startswith('CON '))
        self.assertTrue(CustomUser.objects.filter(id=user.id).exists())

    def test_opportunity_listing_and_application(self):
        self.register()
        service = self.service('opportunity')
        response = service.handle('3')
        self.assertIn('Digital Skills Scholarship', response)
        response = service.handle('1')
        self.assertIn('1. Apply', response)
        response = service.handle('1')
        self.assertTrue(response.startswith('END '))
        self.assertEqual(Application.objects.count(), 1)

    def test_programme_status(self):
        self.register()
        user = CustomUser.objects.get(phone_number=self.phone)
        BeneficiaryParticipation.objects.create(
            beneficiary=user, programme=self.programme,
            participation_status=BeneficiaryParticipation.Status.ACTIVE,
            attendance_rate=80,
        )
        service = self.service('programme')
        service.handle('4')
        response = service.handle('1')
        self.assertIn('Active', response)

    def test_challenge_reporting_marks_ussd_in_audit_history(self):
        self.register()
        user = CustomUser.objects.get(phone_number=self.phone)
        BeneficiaryParticipation.objects.create(beneficiary=user, programme=self.programme)
        service = self.service('challenge')
        service.handle('6')
        response = service.handle('1')
        self.assertTrue(response.startswith('END '))
        challenge = Challenge.objects.get(beneficiary=user)
        self.assertEqual(challenge.status, Challenge.Status.OPEN)
        self.assertEqual(challenge.audit_history[0]['note'], 'Source: USSD')

    def test_invalid_input_keeps_session_open(self):
        response = self.service().handle('99')
        self.assertTrue(response.startswith('CON '))
        self.assertIn('Invalid option', response)

    def test_expired_session_ends_safely(self):
        session = UssdSession.objects.create(
            session_id='expired', phone_number=self.phone,
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        response = self.service('expired').handle('1')
        self.assertTrue(response.startswith('END '))
        self.assertFalse(UssdSession.objects.filter(id=session.id).exists())

    def test_callback_accepts_africas_talking_form_payload(self):
        request = self.client.post('/api/ussd/callback/', {
            'sessionId': 'callback-session',
            'serviceCode': '*123#',
            'phoneNumber': self.phone,
            'networkCode': 'network',
            'text': '',
        })
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request['Content-Type'], 'text/plain')
        self.assertTrue(request.content.decode().startswith('CON '))
