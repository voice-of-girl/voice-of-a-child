"""Seed realistic demo data covering the full platform journey.

Run:  python manage.py seed_demo
Idempotent: re-running skips steps that already have data.
"""
import datetime
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.monitoring.models import Challenge
from apps.organisations.models import Organisation
from apps.participants.models import Participant
from apps.programmes.models import (
    Programme,
    ProgrammeEnrollment,
    ProgrammeKPI,
    ProgrammeObjective,
)
from apps.surveys.models import Answer, Question, Survey, SurveyAssignment, SurveyResponse

ADMIN_EMAIL = "admin@voiceofagirl.org"
ADMIN_PASSWORD = "Admin@2026!"
ORG_EMAIL = "org@brightfuture.org"
ORG_PASSWORD = "Org@2026!"
ORG2_EMAIL = "org@risinghope.org"
ORG2_PASSWORD = "Org@2026!"

PARTICIPANTS = [
    ("Sarah Nakato", 2004, "Kampala", "SECONDARY_O_LEVEL", ["Basic computer"], "Tailoring", "UNEMPLOYED"),
    ("Grace Auma", 2003, "Gulu", "SECONDARY_A_LEVEL", ["Baking"], "Catering business", "UNEMPLOYED"),
    ("Mary Akello", 2005, "Lira", "PRIMARY", [], "Hairdressing", "UNEMPLOYED"),
    ("Joan Nabukenya", 2002, "Kampala", "VOCATIONAL", ["Sewing"], "Fashion design", "SELF_EMPLOYED"),
    ("Esther Kirabo", 2004, "Jinja", "SECONDARY_O_LEVEL", ["Mobile money"], "Accounting", "UNEMPLOYED"),
    ("Rebecca Atim", 2003, "Soroti", "DIPLOMA", ["Data entry"], "IT support", "PART_TIME"),
    ("Patricia Nabirye", 2005, "Masaka", "SECONDARY_O_LEVEL", ["Beadwork"], "Jewellery business", "STUDENT"),
    ("Christine Adong", 2002, "Kitgum", "SECONDARY_A_LEVEL", ["Farming"], "Agribusiness", "SELF_EMPLOYED"),
    ("Betty Namusoke", 2004, "Mbarara", "PRIMARY", [], "Shop keeping", "UNEMPLOYED"),
    ("Doreen Achieng", 2003, "Arua", "SECONDARY_O_LEVEL", ["Phone repair"], "Electronics", "UNEMPLOYED"),
    ("Fiona Kabugho", 2005, "Kasese", "SECONDARY_O_LEVEL", ["Photography"], "Media", "STUDENT"),
    ("Zainab Nabbosa", 2002, "Kampala", "VOCATIONAL", ["Catering"], "Restaurant", "PART_TIME"),
]

# question_text -> (type, options, baseline values, endline values)
INDICATORS = {
    "Are you currently employed or running a business?": (
        "YES_NO",
        [],
        ["No", "No", "Yes", "No", "No", "No", "No", "Yes", "No", "No", "No", "Yes"],
        ["Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "Yes", "No", "Yes", "No", "Yes"],
    ),
    "How many hours per week do you spend on income-generating activities?": (
        "NUMBER",
        [],
        [0, 2, 0, 10, 3, 8, 0, 12, 0, 4, 0, 9],
        [15, 12, 4, 20, 14, 8, 10, 22, 5, 16, 6, 18],
    ),
    "Rate your confidence in using digital tools (1 = low, 5 = high)": (
        "RATING",
        [],
        [1, 2, 1, 3, 2, 3, 1, 3, 1, 2, 1, 3],
        [4, 4, 3, 5, 4, 4, 4, 5, 3, 4, 3, 5],
    ),
}

CHALLENGES = [
    ("TRANSPORT", "Sarah cannot afford daily transport to the training centre.", "RESOLVED"),
    ("FINANCIAL", "Grace lacks startup capital for her baking business.", "IN_PROGRESS"),
    ("ATTENDANCE", "Mary misses sessions during planting season.", "OPEN"),
    ("MATERIALS", "Training centre has only 5 laptops for 12 learners.", "OPEN"),
    ("TRANSPORT", "Fuel costs increased; pickup service is unsustainable.", "IN_PROGRESS"),
]


class Command(BaseCommand):
    help = "Seed demo data for the REACH -> MANAGE -> MONITOR -> MEASURE -> REPORT journey."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Voice of a Girl demo data...")
        self._admin()
        org, org_user = self._organisation("Bright Future Girls Initiative", ORG_EMAIL)
        self._organisation("Rising Hope Foundation", ORG2_EMAIL)

        participants = self._participants(org)
        programme = self._programme(org, org_user)
        self._enrollments(programme, participants)
        self._surveys(programme, org, org_user, participants)
        self._challenges(org, programme, participants, org_user)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write("")
        self.stdout.write("Demo credentials:")
        self.stdout.write(f"  ADMIN         {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        self.stdout.write(f"  ORGANISATION  {ORG_EMAIL} / {ORG_PASSWORD}")
        self.stdout.write(f"  ORGANISATION  {ORG2_EMAIL} / {ORG2_PASSWORD}")

    def _admin(self):
        if CustomUser.objects.filter(email=ADMIN_EMAIL).exists():
            self.stdout.write("Admin already exists - skipped.")
            return
        CustomUser.objects.create_superuser(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            first_name="Platform",
            last_name="Admin",
        )
        self.stdout.write(f"Created admin {ADMIN_EMAIL}")

    def _organisation(self, name, email):
        organisation, created = Organisation.objects.get_or_create(
            name=name,
            defaults={
                "organisation_type": "NGO",
                "contact_person": "Programme Coordinator",
                "email": email,
                "phone_number": "+256700000000",
                "address": "Plot 12, Kampala Road",
                "district": "Kampala",
                "status": Organisation.Status.ACTIVE,
            },
        )
        if created:
            self.stdout.write(f"Created organisation {name}")
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            CustomUser.objects.create_user(
                email=email,
                password=ORG_PASSWORD,
                first_name="Programme",
                last_name="Coordinator",
                role=CustomUser.Role.ORGANISATION,
                organisation=organisation,
                is_verified=True,
            )
            self.stdout.write(f"Created organisation user {email}")
        return organisation, user

    def _participants(self, org):
        if Participant.objects.filter(organisation=org).count() >= len(PARTICIPANTS):
            self.stdout.write("Participants already exist - skipped.")
            return list(org.participants.order_by("id"))
        participants = []
        for name, birth_year, district, education, skills, goal, employment in PARTICIPANTS:
            participant, _ = Participant.objects.get_or_create(
                full_name=name,
                organisation=org,
                defaults={
                    "date_of_birth": datetime.date(birth_year, 6, 15),
                    "gender": Participant.Gender.FEMALE,
                    "phone_number": f"+25677{random.randint(1000000, 9999999)}",
                    "district": district,
                    "region": "Central" if district == "Kampala" else "Northern",
                    "education_level": education,
                    "skills": skills,
                    "interests": ["Entrepreneurship", "Digital skills"],
                    "career_goals": goal,
                    "employment_status": employment,
                    "registration_source": "Voice of a Girl community form",
                    "verification_status": Participant.VerificationStatus.VERIFIED,
                },
            )
            participants.append(participant)
        self.stdout.write(f"Ensured {len(participants)} participants")
        return participants

    def _programme(self, org, org_user):
        programme = Programme.objects.filter(
            title="Digital Skills for Girls", organisation=org
        ).first()
        if programme:
            self.stdout.write("Programme already exists - skipped.")
            return programme
        today = timezone.now().date()
        programme = Programme.objects.create(
            organisation=org,
            title="Digital Skills for Girls",
            description=(
                "A six-month programme equipping out-of-school girls with digital "
                "literacy, online freelancing and entrepreneurship skills."
            ),
            category="Digital Inclusion",
            location="Kampala, Uganda",
            start_date=today - datetime.timedelta(days=120),
            end_date=today + datetime.timedelta(days=60),
            status=Programme.Status.ACTIVE,
            target_participants=15,
            created_by=org_user,
        )
        ProgrammeObjective.objects.create(
            programme=programme,
            title="Train 15 girls in basic digital literacy",
            order=0,
        )
        ProgrammeObjective.objects.create(
            programme=programme,
            title="Connect at least 50% of graduates to income opportunities",
            order=1,
        )
        ProgrammeKPI.objects.create(
            programme=programme,
            name="Girls trained",
            category=ProgrammeKPI.Category.OUTPUT,
            unit="participants",
            target_value=15,
            current_value=12,
            baseline_value=0,
        )
        ProgrammeKPI.objects.create(
            programme=programme,
            name="Employment rate",
            category=ProgrammeKPI.Category.OUTCOME,
            unit="%",
            target_value=50,
            current_value=43,
            baseline_value=21,
            measurement_frequency="Per cohort",
        )
        self.stdout.write("Created programme with objectives and KPIs")
        return programme

    def _enrollments(self, programme, participants):
        if programme.enrollments.exists():
            self.stdout.write("Enrollments already exist - skipped.")
            return
        statuses = (
            [ProgrammeEnrollment.Status.ACTIVE] * 8
            + [ProgrammeEnrollment.Status.COMPLETED] * 2
            + [ProgrammeEnrollment.Status.DROPPED_OUT] * 2
        )
        for participant, status in zip(participants, statuses):
            ProgrammeEnrollment.objects.create(
                programme=programme,
                participant=participant,
                status=status,
                progress=100.0 if status == "COMPLETED" else round(random.uniform(40, 85), 1),
                completed_at=timezone.now() if status == "COMPLETED" else None,
                outcome_notes=(
                    "Completed all modules and submitted final project."
                    if status == "COMPLETED"
                    else ""
                ),
            )
        self.stdout.write(f"Enrolled {len(participants)} participants")

    def _surveys(self, programme, org, org_user, participants):
        for survey_type, title, description, values_index in (
            (
                Survey.SurveyType.BASELINE,
                "Digital Skills Baseline Survey",
                "Collected before training begins.",
                2,
            ),
            (
                Survey.SurveyType.ENDLINE,
                "Digital Skills Endline Survey",
                "Collected after training completion.",
                3,
            ),
        ):
            survey = Survey.objects.filter(title=title, organisation=org).first()
            if not survey:
                survey = Survey.objects.create(
                    organisation=org,
                    title=title,
                    description=description,
                    survey_type=survey_type,
                    programme=programme,
                    status=Survey.Status.PUBLISHED,
                    created_by=org_user,
                )
                for order, (text, spec) in enumerate(INDICATORS.items()):
                    Question.objects.create(
                        survey=survey,
                        question_text=text,
                        question_type=spec[0],
                        options=spec[1],
                        order=order,
                    )
                self.stdout.write(f"Created {survey_type} survey with questions")

            if survey.responses.filter(submitted=True).exists():
                continue
            questions = list(survey.questions.order_by("order"))
            for index, participant in enumerate(participants):
                response = SurveyResponse.objects.create(
                    survey=survey,
                    participant=participant,
                    organisation=org,
                )
                SurveyAssignment.objects.get_or_create(
                    survey=survey, participant=participant
                )
                for question in questions:
                    values = INDICATORS[question.question_text][values_index]
                    Answer.objects.create(
                        response=response,
                        question=question,
                        value=values[index],
                    )
                response.submitted = True
                response.submitted_at = timezone.now()
                response.save()
            self.stdout.write(f"Submitted {len(participants)} responses for {survey_type}")

        # One pending public link on the endline survey (demo of the share flow).
        endline = Survey.objects.get(title="Digital Skills Endline Survey", organisation=org)
        if not endline.responses.filter(submitted=False).exists():
            pending = SurveyResponse.objects.create(survey=endline, organisation=org)
            self.stdout.write(
                f"Pending public link: /api/surveys/link/{pending.access_token}/"
            )

    def _challenges(self, org, programme, participants, org_user):
        if Challenge.objects.filter(organisation=org).exists():
            self.stdout.write("Challenges already exist - skipped.")
            return
        now = timezone.now()
        for index, (category, description, status) in enumerate(CHALLENGES):
            Challenge.objects.create(
                organisation=org,
                programme=programme,
                participant=participants[index % len(participants)],
                category=category,
                description=description,
                status=status,
                date_reported=now - datetime.timedelta(days=30 - index * 3),
                date_resolved=now - datetime.timedelta(days=10) if status == "RESOLVED" else None,
                resolution_notes="Provided transport stipend." if status == "RESOLVED" else "",
                reported_by=org_user,
            )
        self.stdout.write(f"Recorded {len(CHALLENGES)} monitoring challenges")