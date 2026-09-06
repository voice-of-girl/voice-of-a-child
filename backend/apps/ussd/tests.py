from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.monitoring.models import Challenge
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import Programme, ProgrammeEnrollment
from apps.surveys.models import Question, Survey

from .models import UssdSession
from .services import UssdService


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
            category='SKILLS',
            location='Kampala',
            start_date='2026-01-01',
            end_date='2026-12-31',
            status=Programme.Status.ACTIVE,
        )

    def service(self, session='test-session'):
        return UssdService(session, self.phone, '*123#', 'network')

    def register(self, session='registration'):
        service = self.service(session)
        service.handle('')      # main menu
        service.handle('1')     # register
        service.handle('Jane Doe')
        service.handle('Kampala')
        service.handle('2')     # Secondary education
        service.handle('Python, Design')
        return service.handle('Technology, Leadership')

    def enroll(self):
        participant = Participant.objects.get(phone_number=self.phone)
        return ProgrammeEnrollment.objects.create(
            programme=self.programme,
            participant=participant,
            status=ProgrammeEnrollment.Status.ACTIVE,
            progress=60.0,
        )

    def test_initial_request_returns_main_menu(self):
        response = self.service().handle('')
        self.assertTrue(response.startswith('CON '))
        self.assertIn('1. Register', response)
        self.assertIn('4. Check-in', response)

    def test_registration_creates_phone_identified_participant(self):
        response = self.register()
        self.assertTrue(response.startswith('END '))
        self.assertIn('Registration successful', response)
        participant = Participant.objects.get(phone_number=self.phone)
        self.assertEqual(participant.full_name, 'Jane Doe')
        self.assertEqual(participant.district, 'Kampala')
        self.assertEqual(participant.skills, ['Python', 'Design'])
        self.assertEqual(participant.registration_source, 'USSD')
        self.assertEqual(
            participant.verification_status, Participant.VerificationStatus.PENDING
        )
        self.assertIsNone(participant.organisation)

    def test_existing_participant_is_not_reregistered(self):
        self.register('first-session')
        service = self.service('second-session')
        service.handle('')
        response = service.handle('1')
        self.assertIn('already registered', response)
        self.assertEqual(Participant.objects.filter(phone_number=self.phone).count(), 1)

    def test_programme_status_and_progress(self):
        self.register('reg')
        self.enroll()
        service = self.service('programme')
        service.handle('')
        service.handle('3')          # My Programme
        response = service.handle('1')   # Programme Status
        self.assertIn('Status: Active', response)

        service2 = self.service('progress')
        service2.handle('')
        service2.handle('3')
        response = service2.handle('2')  # My Progress
        self.assertIn('Progress: 60%', response)

    def test_checkin_records_survey_response(self):
        self.register('reg')
        self.enroll()
        survey = Survey.objects.create(
            organisation=self.organisation,
            title='Weekly Check-in',
            survey_type=Survey.SurveyType.MONITORING,
            programme=self.programme,
            status=Survey.Status.PUBLISHED,
        )
        question = Question.objects.create(
            survey=survey,
            question_text='How is the programme going?',
            question_type=Question.QuestionType.RATING,
            order=0,
        )
        service = self.service('checkin')
        service.handle('')
        service.handle('4')      # Check-in
        service.handle('2')      # Good
        response = service.handle('2')   # No further challenges
        self.assertTrue(response.startswith('END '))
        from apps.surveys.models import Answer, SurveyResponse
        survey_response = SurveyResponse.objects.get(survey=survey)
        self.assertTrue(survey_response.submitted)
        self.assertEqual(Answer.objects.get(response=survey_response).value, 'Good')

    def test_challenge_reporting_creates_open_challenge(self):
        self.register('reg')
        self.enroll()
        service = self.service('challenge')
        service.handle('')
        service.handle('5')      # Report Challenge
        service.handle('2')      # Financial
        response = service.handle('Cannot pay for internet data')
        self.assertTrue(response.startswith('END '))
        challenge = Challenge.objects.get(
            organisation=self.organisation, category=Challenge.Category.FINANCIAL
        )
        self.assertEqual(challenge.status, Challenge.Status.OPEN)
        self.assertEqual(challenge.participant.phone_number, self.phone)
        self.assertIn('USSD', challenge.description)

    def test_invalid_input_keeps_session_open(self):
        response = self.service().handle('99')
        self.assertTrue(response.startswith('CON '))
        self.assertIn('Invalid option', response)

    def test_expired_session_ends_safely(self):
        service = self.service('expired')
        service.handle('')
        session = UssdSession.objects.get(session_id='expired')
        session.expires_at = timezone.now() - timedelta(minutes=1)
        session.save(update_fields=['expires_at'])
        response = service.handle('1')
        self.assertTrue(response.startswith('END '))
        self.assertIn('expired', response)

    def test_callback_accepts_africas_talking_form_payload(self):
        response = self.client.post(
            '/api/ussd/callback/',
            {
                'sessionId': 'ATUid_12345',
                'phoneNumber': self.phone,
                'serviceCode': '*123#',
                'networkCode': '99999',
                'text': '',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.decode().startswith('CON '))
        self.assertTrue(UssdSession.objects.filter(session_id='ATUid_12345').exists())

    def test_callback_rejects_missing_phone(self):
        response = self.client.post('/api/ussd/callback/', {'sessionId': 'x', 'text': ''})
        self.assertEqual(response.status_code, 400)
