import re
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application
from apps.beneficiaries.models import BeneficiaryProfile
from apps.challenges.models import Challenge
from apps.forms.models import Form, FormAnswer, FormResponse
from apps.opportunities.models import Opportunity
from apps.participation.models import BeneficiaryParticipation
from apps.programmes.models import Programme
from apps.accounts.models import CustomUser

from .models import UssdSession


class UssdService:
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
            if not session.completed:
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
        if session.state == UssdSession.State.OPPORTUNITIES:
            return self._opportunity_choice(session, choice)
        if session.state == UssdSession.State.OPPORTUNITY_DETAIL:
            return self._opportunity_detail(session, choice)
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
        return self._continue('Welcome to Voice of a Girl\n1. Register\n2. Login/Profile\n3. Opportunities\n4. My Programme\n5. Check-in\n6. Report Challenge')

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
            return self._opportunities(session)
        if choice == '4':
            return self._programme(session)
        if choice == '5':
            return self._checkin(session)
        if choice == '6':
            session.state = UssdSession.State.CHALLENGE
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('Report Challenge\n1. Transport\n2. Financial\n3. Attendance\n4. Materials\n5. Other\n0. Back')
        return self._continue('Invalid option. Please choose 1 to 6.')

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
        education = {'1': 'PRIMARY', '2': 'SECONDARY_O_LEVEL', '3': 'VOCATIONAL_CERTIFICATE', '4': 'DIPLOMA', '5': 'BACHELORS'}.get(value)
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
        user = self._participant()
        if not user:
            email = f"{self._phone_slug()}@ussd.voiceofagirl.local"
            user = CustomUser.objects.create_user(
                email=email,
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=self.phone_number,
                role=CustomUser.Role.BENEFICIARY,
            )
        else:
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save(update_fields=['first_name', 'last_name', 'updated_at'])
        BeneficiaryProfile.objects.update_or_create(
            user=user,
            defaults={
                'district': data['district'],
                'education_level': data['education_level'],
                'skills': data['skills'],
                'interests': data['interests'],
                'profile_completed': True,
            },
        )
        session.temporary_data = {}
        session.completed = True
        session.state = UssdSession.State.MENU
        session.save(update_fields=['temporary_data', 'completed', 'state', 'updated_at'])
        return self._end('Registration successful. Thank you for joining Voice of a Girl.')

    def _opportunities(self, session):
        opportunities = list(Opportunity.objects.filter(status=Opportunity.Status.OPEN).select_related('programme')[:3])
        session.temporary_data['opportunity_ids'] = [opportunity.id for opportunity in opportunities]
        session.state = UssdSession.State.OPPORTUNITIES
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        if not opportunities:
            return self._continue('No open opportunities are available right now.\n0. Back')
        lines = ['Opportunities'] + [f'{index}. {opportunity.title[:48]}' for index, opportunity in enumerate(opportunities, 1)] + ['0. Back']
        return self._continue('\n'.join(lines))

    def _opportunity_choice(self, session, choice):
        if choice == '0':
            return self._menu(session)
        ids = session.temporary_data.get('opportunity_ids', [])
        try:
            opportunity = Opportunity.objects.get(id=ids[int(choice) - 1], status=Opportunity.Status.OPEN)
        except (ValueError, IndexError, Opportunity.DoesNotExist):
            return self._continue('Invalid opportunity. Choose a listed number or 0 to go back.')
        session.temporary_data['opportunity_id'] = opportunity.id
        session.state = UssdSession.State.OPPORTUNITY_DETAIL
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue(f'{opportunity.title}\n{opportunity.description[:120]}\n1. Apply\n2. Back')

    @transaction.atomic
    def _opportunity_detail(self, session, choice):
        if choice == '2':
            return self._opportunities(session)
        if choice != '1':
            return self._continue('Invalid option. Choose 1 to apply or 2 to go back.')
        user = self._participant()
        if not user:
            session.state = UssdSession.State.REGISTER_NAME
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('Please register first. Enter your full name:')
        opportunity = Opportunity.objects.get(id=session.temporary_data['opportunity_id'])
        Application.objects.get_or_create(beneficiary=user, opportunity=opportunity)
        session.state = UssdSession.State.MENU
        session.save(update_fields=['state', 'updated_at'])
        return self._end('Application received. The organisation will review your profile.')

    def _programme(self, session):
        user = self._participant()
        participation = BeneficiaryParticipation.objects.filter(beneficiary=user).select_related('programme').first() if user else None
        session.temporary_data['programme_id'] = participation.programme_id if participation else None
        session.state = UssdSession.State.PROGRAMME
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        if not participation:
            return self._continue('No active programme found.\n0. Back')
        return self._continue(f'My Programme\n{participation.programme.title[:55]}\n1. Programme Status\n2. Next Activity\n3. My Progress\n0. Back')

    def _programme_choice(self, session, choice):
        if choice == '0':
            return self._menu(session)
        programme_id = session.temporary_data.get('programme_id')
        participation = BeneficiaryParticipation.objects.filter(programme_id=programme_id, beneficiary=self._participant()).select_related('programme').first()
        if not participation:
            return self._continue('No programme record found.\n0. Back')
        if choice == '1':
            return self._continue(f'Status: {participation.get_participation_status_display()}\nProgramme: {participation.programme.title[:55]}\n0. Back')
        if choice == '2':
            return self._continue('Next activity information is available from your programme team.\n0. Back')
        if choice == '3':
            return self._continue(f'Progress: {participation.attendance_rate:.0f}% attendance\nStatus: {participation.get_participation_status_display()}\n0. Back')
        return self._continue('Invalid option. Choose 1, 2, 3, or 0.')

    def _checkin(self, session):
        user = self._participant()
        participation = BeneficiaryParticipation.objects.filter(beneficiary=user).select_related('programme').first() if user else None
        if not participation:
            return self._continue('You need an active programme before completing a check-in.\n0. Back')
        form = Form.objects.filter(programme=participation.programme, form_type=Form.FormType.MONITORING, status=Form.Status.PUBLISHED).prefetch_related('questions').first()
        session.temporary_data['programme_id'] = participation.programme_id
        session.temporary_data['form_id'] = form.id if form else None
        session.state = UssdSession.State.CHECKIN
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('Programme Check-in\nHow is the programme going?\n1. Very Good\n2. Good\n3. Okay\n4. Difficult')

    def _checkin_answer(self, session, choice):
        if choice not in {'1', '2', '3', '4'}:
            return self._continue('Invalid option. Choose 1 Very Good, 2 Good, 3 Okay, or 4 Difficult.')
        session.temporary_data['checkin_rating'] = choice
        session.state = UssdSession.State.CHECKIN_CHALLENGE
        session.save(update_fields=['temporary_data', 'state', 'updated_at'])
        return self._continue('Are you facing a challenge?\n1. Yes\n2. No')

    def _checkin_challenge(self, session, choice):
        if choice == '2':
            self._save_checkin(session)
            return self._end('Thank you. Your check-in was recorded.')
        if choice == '1':
            session.state = UssdSession.State.CHECKIN_CATEGORY
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('What type?\n1. Transport\n2. Financial\n3. Attendance\n4. Materials\n5. Other')
        return self._continue('Invalid option. Choose 1 Yes or 2 No.')

    def _checkin_category(self, session, choice):
        category = self._category(choice)
        if not category:
            return self._continue('Invalid option. Choose 1 Transport, 2 Financial, 3 Attendance, 4 Materials, or 5 Other.')
        session.temporary_data['challenge_category'] = category
        self._save_checkin(session)
        self._create_challenge(category, 'Challenge reported during USSD programme check-in.')
        return self._end('Thank you. Your check-in and challenge were recorded.')

    def _save_checkin(self, session):
        form_id = session.temporary_data.get('form_id')
        user = self._participant()
        if not form_id or not user:
            return
        form = Form.objects.filter(id=form_id, status=Form.Status.PUBLISHED).first()
        if not form:
            return
        response, _ = FormResponse.objects.get_or_create(form=form, beneficiary=user, defaults={'submitted_via': 'USSD'})
        response.status = FormResponse.Status.SUBMITTED
        response.submitted_at = timezone.now()
        response.submitted_via = 'USSD'
        response.save(update_fields=['status', 'submitted_at', 'submitted_via'])
        question = form.questions.first()
        if question:
            FormAnswer.objects.update_or_create(
                response=response,
                question=question,
                defaults={'value': session.temporary_data.get('checkin_rating', '')},
            )

    def _challenge_choice(self, session, choice):
        if choice == '0':
            return self._menu(session)
        category = self._category(choice)
        if not category:
            return self._continue('Invalid option. Choose 1 Transport, 2 Financial, 3 Attendance, 4 Materials, or 5 Other.')
        if not self._participant():
            return self._continue('Please register first by choosing 1 from the main menu.')
        self._create_challenge(category, 'Challenge reported through USSD.')
        session.state = UssdSession.State.MENU
        session.save(update_fields=['state', 'updated_at'])
        return self._end('Your challenge was recorded. A programme officer will follow up.')

    def _profile_choice(self, session, choice):
        user = self._participant()
        if choice == '0':
            return self._menu(session)
        if choice == '1':
            if not user:
                return self._continue('No profile found. Choose 2 to update or 0 to go back.')
            profile = getattr(user, 'beneficiary_profile', None)
            if not profile:
                return self._continue('No profile found. Choose 2 to update or 0 to go back.')
            return self._continue(f'{user.first_name} {user.last_name}\n{profile.district}\n{profile.get_education_level_display()}\n1. View profile\n2. Update profile\n0. Back')
        if choice == '2':
            session.state = UssdSession.State.PROFILE_LOCATION
            session.save(update_fields=['state', 'updated_at'])
            return self._continue('Enter your current district or location:')
        return self._continue('Invalid option. Choose 1, 2, or 0.')

    def _profile_update(self, session, value):
        if session.state == UssdSession.State.PROFILE_LOCATION:
            session.temporary_data['district'] = value
            session.state = UssdSession.State.PROFILE_EDUCATION
            prompt = 'Education level:\n1. Primary\n2. Secondary\n3. Vocational\n4. Diploma\n5. Degree'
        elif session.state == UssdSession.State.PROFILE_EDUCATION:
            education = {'1': 'PRIMARY', '2': 'SECONDARY_O_LEVEL', '3': 'VOCATIONAL_CERTIFICATE', '4': 'DIPLOMA', '5': 'BACHELORS'}.get(value)
            if not education:
                return self._continue('Invalid option. Choose an education option from 1 to 5.')
            session.temporary_data['education_level'] = education
            session.state = UssdSession.State.PROFILE_SKILLS
            prompt = 'List your main skills, separated by commas:'
        elif session.state == UssdSession.State.PROFILE_SKILLS:
            session.temporary_data['skills'] = self._list_input(value)
            session.state = UssdSession.State.PROFILE_INTERESTS
            prompt = 'What interests you? Separate interests with commas:'
        else:
            session.temporary_data['interests'] = self._list_input(value)
            user = self._participant()
            if user:
                profile, _ = BeneficiaryProfile.objects.get_or_create(user=user, defaults={'district': session.temporary_data.get('district', 'Unknown')})
                for field in ('district', 'education_level', 'skills', 'interests'):
                    if field in session.temporary_data:
                        setattr(profile, field, session.temporary_data[field])
                profile.profile_completed = True
                profile.save()
            session.state = UssdSession.State.MENU
            session.temporary_data = {}
            session.save(update_fields=['state', 'temporary_data', 'updated_at'])
            return self._end('Your profile was updated successfully.')
        session.save(update_fields=['state', 'temporary_data', 'updated_at'])
        return self._continue(prompt)

    def _participant(self) -> Optional[CustomUser]:
        return CustomUser.objects.filter(phone_number=self.phone_number, role=CustomUser.Role.BENEFICIARY).first()

    def _create_challenge(self, category, description):
        user = self._participant()
        if not user:
            return
        participation = BeneficiaryParticipation.objects.filter(beneficiary=user).select_related('programme').first()
        if not participation:
            return
        challenge = Challenge.objects.create(
            programme=participation.programme,
            beneficiary=user,
            category=category,
            description=description,
            status=Challenge.Status.OPEN,
            severity=Challenge.Severity.MEDIUM,
            audit_history=[{'timestamp': timezone.now().isoformat(), 'actor': 'USSD', 'action': 'Reported', 'note': 'Source: USSD'}],
        )
        return challenge

    @staticmethod
    def _category(choice):
        return {'1': Challenge.Category.TRANSPORT, '2': Challenge.Category.FINANCIAL, '3': Challenge.Category.ATTENDANCE, '4': Challenge.Category.MATERIALS, '5': Challenge.Category.OTHER}.get(choice)

    @staticmethod
    def _list_input(value):
        return [item.strip()[:80] for item in value.split(',') if item.strip()][:10]

    @staticmethod
    def _clean(value, max_length):
        value = re.sub(r'[\r\n\x00]', ' ', str(value or '')).strip()
        return value[:max_length]

    def _phone_slug(self):
        return re.sub(r'[^0-9]', '', self.phone_number)[-20:] or 'unknown'

    @staticmethod
    def _continue(message):
        return f'CON {message}'

    def _end(self, message):
        try:
            session = UssdSession.objects.get(session_id=self.session_id)
            session.completed = True
            session.save(update_fields=['completed', 'updated_at'])
        except UssdSession.DoesNotExist:
            pass
        return f'END {message}'
