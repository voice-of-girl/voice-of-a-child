import re
from datetime import timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.monitoring.models import Challenge
from apps.participants.models import Participant
from apps.programmes.models import ProgrammeEnrollment
from apps.surveys.models import Answer, Survey, SurveyResponse

from .models import UssdSession

RATING_LABELS = {'1': 'Very Good', '2': 'Good', '3': 'Okay', '4': 'Difficult'}


class UssdService:
    """Africa's Talking USSD flows mapped onto the Voice of a Girl data model.

    Participants do NOT have user accounts - registration creates a
    Participant record (organisation-agnostic, PENDING) keyed by phone number.
    """

    SESSION_TTL = timedelta(minutes=15)
    MAX_INPUT_LENGTH = 500

    def __init__(self, session_id: str, phone_number: str, service_code: str = '', network_code: str = ''):
        self.session_id = self._clean(session_id, 120)
        self.phone_number = self._clean(phone_number, 30)
        self.service_code = self._clean(service_code, 30)
        self.network_code = self._clean(network_code, 80)

    def handle(self, text: str) -> str:
        try:
            session = self._get_session()
            if session.completed:
                return self._end('This USSD session is already complete. Please dial again to start a new session.')
            if session.is_expired():
                session.delete()
                return self._end('Your session expired. Please dial again to continue.')

            value = self._clean(text, self.MAX_INPUT_LENGTH)
            if not value:
                return self._menu(session)

            return self._dispatch(session, value.split('*')[-1].strip())
        except Exception:
            return self._end('Sorry, we are unable to process your request right now. Please try again later.')

    def _get_session(self) -> UssdSession:
        now = timezone.now()
        session = UssdSession.objects.filter(session_id=self.session_id).first()
        if session:
            if session.phone_number != self.phone_number:
                raise ValueError('USSD session phone mismatch')
            if not session.completed and not session.is_expired():
                session.expires_at = now + self.SESSION_TTL
                session.save(update_fields=['expires_at', 'updated_at'])
            return session
        session = UssdSession.objects.create(
            session_id=self.session_id,
            phone_number=self.phone_number,
            service_code=self.service_code,
            network_code=self.network_code,
            expires_at=now + self.SESSION_TTL,
        )
        return session

    def _dispatch(self, session: UssdSession, choice: str) -> str:
        if session.state == UssdSession.State.MENU:
            return self._menu_choice(session, choice)
        if session.state == UssdSession.State.REGISTER_NAME:
            return self._registration_name(session, choice)
        if session.state == UssdSession.State.REGISTER_LOCATION:
            return self._registration_location(session, choice)
        if session.state == UssdSession.State.REGISTER_EDUCATION:
            return self._registration_education(session, choice)
        if session.state == UssdSession.State.REGISTER_SKILLS:
            return self._registration_skills(session, choice)
        if session.state == UssdSession.State.REGISTER_INTERESTS:
            return self._registration_interests(session, choice)
        if session.state == UssdSession.State.PROGRAMME:
            return self._programme_choice(session, choice)
        if session.state == UssdSession.State.CHECKIN:
            return self._checkin_answer(session, choice)
        if session.state == UssdSession.State.CHECKIN_CHALLENGE:
            return self._checkin_challenge(session, choice)
        if session.state == UssdSession.State.CHECKIN_CATEGORY:
            return self._checkin_category(session, choice)
        if session.state == UssdSession.State.CHALLENGE:
            return self._challenge_choice(session, choice)
        if session.state == UssdSession.State.PROFILE:
            return self._profile_choice(session, choice)
        if session.state in {UssdSession.State.PROFILE_LOCATION, UssdSession.State.PROFILE_EDUCATION,
                             UssdSession.State.PROFILE_SKILLS, UssdSession.State.PROFILE_INTERESTS}:
            return self._profile_update(session, choice)
        return self._menu(session)

    def _menu(self, session):
        session.state = UssdSession.State.MENU
        session.save(update_fields=['state', 'updated_at'])
        return self._continue('Welcome to Voice of a Girl\n1. Register\n2. My Profile\n3. My Programme\n4. Check-in\n5. Report Challenge')

    def _menu_choice(self, session, choice):
        if choice == '1':
            if self._participant():
                session.state = UssdSession.State.PROFILE
                session.save(update_fields=['state', 'updated_at'])
                return self._continue('You are already registered.\n1. View profile\n2. Update profile\n0. Back')
            session.state = UssdSession.State.REGISTER_NAME
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('Registration\nEnter your full name:')
        if choice == '2':
            session.state = UssdSession.State.PROFILE
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('My Profile\n1. View profile\n2. Update profile\n0. Back')
        if choice == '3':
            return self._programme(session)
        if choice == '4':
            return self._checkin(session)
        if choice == '5':
            session.state = UssdSession.State.CHALLENGE
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('Report Challenge\n1. Transport\n2. Financial\n3. Attendance\n4. Materials\n5. Other\n0. Back')
        return self._continue('Invalid option. Please choose 1 to 5.')

    @transaction.atomic
    def _registration_name(self, session, value):
        parts = value.split()
        if len(parts) < 2:
            return self._continue('Please enter your first and last name:')
        if self._participant():
            session.state = UssdSession.State.PROFILE_LOCATION
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('You already have a profile. Enter your current district or location to update it:')
        session.temporary_data['first_name'] = parts[0]
        session.temporary_data['last_name'] = ' '.join(parts[1:])
        session.state = UssdSession.State.REGISTER_LOCATION
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('Enter your district or location:')

    def _registration_location(self, session, value):
        session.temporary_data['district'] = value
        session.state = UssdSession.State.REGISTER_EDUCATION
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('Education level:\n1. Primary\n2. Secondary\n3. Vocational\n4. Diploma\n5. Degree')

    def _registration_education(self, session, value):
        education = {
            '1': Participant.EducationLevel.PRIMARY,
            '2': Participant.EducationLevel.SECONDARY_O_LEVEL,
            '3': Participant.EducationLevel.VOCATIONAL,
            '4': Participant.EducationLevel.DIPLOMA,
            '5': Participant.EducationLevel.BACHELORS,
        }.get(value)
        if not education:
            return self._continue('Invalid option. Choose 1 Primary, 2 Secondary, 3 Vocational, 4 Diploma, or 5 Degree.')
        session.temporary_data['education_level'] = education
        session.state = UssdSession.State.REGISTER_SKILLS
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('List your main skills, separated by commas:')

    def _registration_skills(self, session, value):
        session.temporary_data['skills'] = self._list_input(value)
        session.state = UssdSession.State.REGISTER_INTERESTS
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('What interests you? Separate interests with commas:')

    @transaction.atomic
    def _registration_interests(self, session, value):
        data = session.temporary_data
        data['interests'] = self._list_input(value)
        participant = self._participant()
        if participant:
            participant.district = data['district']
            participant.education_level = data['education_level']
            participant.skills = data['skills']
            participant.interests = data['interests']
            participant.save()
        else:
            # Participants never receive accounts; the record stays
            # organisation-agnostic until an organisation claims/verifies it.
            Participant.objects.create(
                full_name=f"{data['first_name']} {data['last_name']}".strip(),
                phone_number=self.phone_number,
                district=data['district'],
                education_level=data['education_level'],
                skills=data['skills'],
                interests=data['interests'],
                registration_source='USSD',
                verification_status=Participant.VerificationStatus.PENDING,
            )
        session.temporary_data = {}
        session.completed = True
        session.state = UssdSession.State.MENU
        session.save(update_fields=['temporary_data', 'completed', 'state', 'updated_at'])
        return self._end('Registration successful. Thank you for joining Voice of a Girl.')

    def _enrollment(self):
        participant = self._participant()
        if not participant:
            return None
        return (
            ProgrammeEnrollment.objects.filter(participant=participant)
            .select_related('programme', 'programme__organisation')
            .first()
        )

    def _programme(self, session):
        enrollment = self._enrollment()
        session.temporary_data['programme_id'] = enrollment.programme_id if enrollment else None
        session.state = UssdSession.State.PROGRAMME
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        if not enrollment:
            return self._continue('No active programme found.\n0. Back')
        return self._continue(
            f'My Programme\n{enrollment.programme.title[:55]}\n'
            '1. Programme Status\n2. My Progress\n0. Back'
        )

    def _programme_choice(self, session, choice):
        if choice == '0':
            return self._menu(session)
        enrollment = ProgrammeEnrollment.objects.filter(
            programme_id=session.temporary_data.get('programme_id'),
            participant=self._participant(),
        ).select_related('programme').first()
        if not enrollment:
            return self._continue('No programme record found.\n0. Back')
        if choice == '1':
            return self._continue(
                f'Status: {enrollment.get_status_display()}\n'
                f'Programme: {enrollment.programme.title[:55]}\n0. Back'
            )
        if choice == '2':
            return self._continue(
                f'Progress: {enrollment.progress:.0f}%\n'
                f'Status: {enrollment.get_status_display()}\n0. Back'
            )
        return self._continue('Invalid option. Choose 1, 2, or 0.')

    def _checkin(self, session):
        enrollment = self._enrollment()
        if not enrollment:
            return self._continue('You need an active programme before completing a check-in.\n0. Back')
        form = (
            Survey.objects.filter(
                programme=enrollment.programme,
                survey_type=Survey.SurveyType.MONITORING,
                status=Survey.Status.PUBLISHED,
            )
            .prefetch_related('questions')
            .first()
        )
        session.temporary_data['programme_id'] = enrollment.programme_id
        session.temporary_data['survey_id'] = form.id if form else None
        session.state = UssdSession.State.CHECKIN
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('Programme Check-in\nHow is the programme going?\n1. Very Good\n2. Good\n3. Okay\n4. Difficult')

    @transaction.atomic
    def _checkin_answer(self, session, choice):
        label = RATING_LABELS.get(choice)
        if not label:
            return self._continue('Invalid option. Choose 1 (Very Good) to 4 (Difficult).')
        survey = Survey.objects.filter(
            id=session.temporary_data.get('survey_id')
        ).select_related('programme__organisation').first()
        participant = self._participant()
        if survey and participant:
            response = SurveyResponse.objects.create(
                survey=survey,
                participant=participant,
                organisation=survey.programme.organisation,
            )
            question = survey.questions.order_by('order').first()
            if question:
                Answer.objects.create(response=response, question=question, value=label)
            response.submitted = True
            response.submitted_at = timezone.now()
            response.save()
        session.temporary_data['checkin_rating'] = label
        session.state = UssdSession.State.CHECKIN_CHALLENGE
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('Thank you for your feedback.\nAny challenges to report?\n1. Yes\n2. No\n0. Back')

    def _checkin_challenge(self, session, choice):
        if choice == '0':
            return self._menu(session)
        if choice == '1':
            session.state = UssdSession.State.CHECKIN_CATEGORY
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('Challenge category:\n1. Transport\n2. Financial\n3. Attendance\n4. Materials\n5. Other\n0. Back')
        if choice == '2':
            session.completed = True
            session.save(update_fields=['completed', 'updated_at'])
            return self._end('Thank you! Your check-in has been recorded.')
        return self._continue('Invalid option. Choose 1 (Yes), 2 (No), or 0 (Back).')

    @transaction.atomic
    def _checkin_category(self, session, choice):
        if choice == '0':
            return self._menu(session)
        category = {
            '1': Challenge.Category.TRANSPORT,
            '2': Challenge.Category.FINANCIAL,
            '3': Challenge.Category.ATTENDANCE,
            '4': Challenge.Category.MATERIALS,
            '5': Challenge.Category.OTHER,
        }.get(choice)
        if not category:
            return self._continue('Invalid option. Choose 1 to 5, or 0 to go back.')
        enrollment = self._enrollment()
        if not enrollment:
            session.completed = True
            session.save(update_fields=['completed', 'updated_at'])
            return self._end('You need an active programme before reporting a challenge. Please contact your coordinator.')
        Challenge.objects.create(
            organisation=enrollment.programme.organisation,
            programme=enrollment.programme,
            participant=self._participant(),
            category=category,
            description=(
                f"Reported via USSD check-in. "
                f"Rating: {session.temporary_data.get('checkin_rating', 'Not provided')}."
            ),
        )
        session.completed = True
        session.save(update_fields=['completed', 'updated_at'])
        return self._end('Your challenge has been reported. Your organisation will follow up. Thank you!')

    def _challenge_choice(self, session, choice):
        if choice == '0':
            return self._menu(session)
        enrollment = self._enrollment()
        if not enrollment:
            return self._continue('You need an active programme before reporting a challenge.\n0. Back')
        category = {
            '1': Challenge.Category.TRANSPORT,
            '2': Challenge.Category.FINANCIAL,
            '3': Challenge.Category.ATTENDANCE,
            '4': Challenge.Category.MATERIALS,
            '5': Challenge.Category.OTHER,
        }.get(choice)
        if not category:
            return self._continue('Invalid option. Choose 1 to 5, or 0 to go back.')
        Challenge.objects.create(
            organisation=enrollment.programme.organisation,
            programme=enrollment.programme,
            participant=self._participant(),
            category=category,
            description='Reported via USSD menu. Details to be confirmed by coordinator.',
        )
        session.completed = True
        session.save(update_fields=['completed', 'updated_at'])
        return self._end('Your challenge has been reported. Your organisation will follow up. Thank you!')

    def _profile_choice(self, session, choice):
        participant = self._participant()
        if choice == '0':
            return self._menu(session)
        if not participant:
            session.completed = True
            session.save(update_fields=['completed', 'updated_at'])
            return self._end('You are not registered yet. Please dial again and choose 1 to register.')
        if choice == '1':
            skills = ', '.join(participant.skills) or 'None'
            interests = ', '.join(participant.interests) or 'None'
            return self._continue(
                f'Profile\n{participant.full_name}\n'
                f'District: {participant.district or "N/A"}\n'
                f'Education: {participant.get_education_level_display()}\n'
                f'Skills: {skills[:80]}\n'
                f'Interests: {interests[:80]}\n0. Back'
            )
        if choice == '2':
            return self._continue(
                'Update profile:\n1. Location\n2. Education\n3. Skills\n4. Interests\n0. Back'
            )
        target_state = {
            '1': UssdSession.State.PROFILE_LOCATION,
            '2': UssdSession.State.PROFILE_EDUCATION,
            '3': UssdSession.State.PROFILE_SKILLS,
            '4': UssdSession.State.PROFILE_INTERESTS,
        }.get(choice)
        if not target_state:
            return self._continue('Invalid option. Choose 1, 2, or 0.')
        session.state = target_state
        session.save(update_fields=['state', 'updated_at'])
        prompts = {
            UssdSession.State.PROFILE_LOCATION: 'Enter your current district or location:',
            UssdSession.State.PROFILE_EDUCATION: 'Education level:\n1. Primary\n2. Secondary\n3. Vocational\n4. Diploma\n5. Degree',
            UssdSession.State.PROFILE_SKILLS: 'List your skills, separated by commas:',
            UssdSession.State.PROFILE_INTERESTS: 'What interests you? Separate with commas:',
        }
        return self._continue(prompts[target_state])

    @transaction.atomic
    def _profile_update(self, session, value):
        participant = self._participant()
        if not participant:
            session.completed = True
            session.save(update_fields=['completed', 'updated_at'])
            return self._end('You are not registered yet. Please dial again and choose 1 to register.')
        state = session.state
        if state == UssdSession.State.PROFILE_LOCATION:
            participant.district = value
        elif state == UssdSession.State.PROFILE_EDUCATION:
            education = {
                '1': Participant.EducationLevel.PRIMARY,
                '2': Participant.EducationLevel.SECONDARY_O_LEVEL,
                '3': Participant.EducationLevel.VOCATIONAL,
                '4': Participant.EducationLevel.DIPLOMA,
                '5': Participant.EducationLevel.BACHELORS,
            }.get(value)
            if not education:
                return self._continue('Invalid option. Choose 1 to 5.')
            participant.education_level = education
        elif state == UssdSession.State.PROFILE_SKILLS:
            participant.skills = self._list_input(value)
        elif state == UssdSession.State.PROFILE_INTERESTS:
            participant.interests = self._list_input(value)
        participant.save()
        session.state = UssdSession.State.MENU
        session.save(update_fields=['state', 'updated_at'])
        return self._continue('Profile updated successfully.\n0. Back')

    # -- helpers ---------------------------------------------------------

    def _participant(self) -> Optional[Participant]:
        return (
            Participant.objects.filter(phone_number=self.phone_number)
            .order_by('-created_at')
            .first()
        )

    def _continue(self, text: str) -> str:
        return f'CON {text}'

    def _end(self, text: str) -> str:
        return f'END {text}'

    def _list_input(self, value: str) -> list:
        return [item.strip() for item in value.split(',') if item.strip()][:20]

    @staticmethod
    def _clean(value: str, max_length: int) -> str:
        return str(value or '').strip()[:max_length]