"""
Seed the database with rich, realistic demo data for a compelling showcase.

Usage:
    python manage.py seed_demo [--fresh]

"Fresh" wipes existing data for the demo organisations first so the command
can be re-run to reset the demo cleanly.

Demo logins (password for every user: Voice@2026!):
    platform_admin@voiceofagirl.org
    admin@voiceofagirl.org
    manager@voiceofagirl.org
    mne@voiceofagirl.org
    staff@voiceofagirl.org
    admin@brightfutures.org
"""
import random
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

DEMO_PASSWORD = "Voice@2026!"


class Command(BaseCommand):
    help = "Seed rich demo data for the Voice of a Girl platform."

    def add_arguments(self, parser):
        parser.add_argument("--fresh", action="store_true", help="Reset demo data first.")

    def handle(self, *args, **options):
        if options["fresh"]:
            _reset()
            self.stdout.write(self.style.WARNING("Existing demo data reset."))

        if _already_seeded():
            self.stdout.write(
                self.style.SUCCESS("Demo data already present. Use --fresh to rebuild.")
            )
            return

        self.stdout.write("Seeding demo data ...")
        org1, org2 = _create_organisations_and_users()
        p1, p2, p3 = _create_programmes(org1)
        _create_org2_programme(org2)
        participants = _create_participants(org1, p1, p2, p3)
        _create_participants_org2(org2)
        _create_org2_surveys(org2)
        surveys = _create_surveys(org1, p1, p2)
        _create_responses(participants, surveys)
        kpis = _create_kpis(org1, p1, p2)
        _create_measurements(org1, p1, kpis)
        _create_monitoring(org1, p1, p2)
        _create_impact_project(org1)
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))


def _already_seeded():
    from apps.organisations.models import Organisation

    return Organisation.objects.filter(name__iexact="Voice of a Girl").exists()


def _reset():
    from apps.organisations.models import Organisation

    Organisation.objects.filter(
        name__in=["Voice of a Girl", "Bright Futures Youth Trust"]
    ).delete()
def _make_user(email, first_name, last_name, role, organisation=None):
    from apps.accounts.models import CustomUser

    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "organisation": organisation,
            "is_active": True,
        },
    )
    if created:
        user.set_password(DEMO_PASSWORD)
        user.save()
    return user


def _create_organisations_and_users():
    from apps.accounts.models import CustomUser
    from apps.organisations.models import Organisation

    org1, _ = Organisation.objects.get_or_create(
        name="Voice of a Girl",
        defaults={
            "description": (
                "An NGO working with adolescent girls and young women across Uganda "
                "to improve education access, digital skills, leadership and economic "
                "opportunity through evidence-based programmes."
            ),
            "organisation_type": "NGO",
            "email": "info@voiceofagirl.org",
            "phone_number": "+256 700 123456",
            "website": "https://voiceofagirl.org",
            "address": "Plot 14, Innovation Way, Bugolobi",
            "district": "Kampala",
            "country": "Uganda",
            "verification_status": "VERIFIED",
        },
    )

    org2, _ = Organisation.objects.get_or_create(
        name="Bright Futures Youth Trust",
        defaults={
            "description": (
                "A youth trust focused on skills-to-work pathways for young people "
                "in central Uganda. Partnering with Voice of a Girl to pilot impact "
                "measurement on the platform."
            ),
            "organisation_type": "COMMUNITY",
            "email": "hello@brightfutures.org",
            "phone_number": "+256 772 555444",
            "address": "Main Road 12",
            "district": "Mukono",
            "country": "Uganda",
            "verification_status": "VERIFIED",
        },
    )

    _make_user("platform_admin@voiceofagirl.org", "Elena", "Vance", CustomUser.Role.PLATFORM_ADMIN, None)
    platform_user = CustomUser.objects.get(email="platform_admin@voiceofagirl.org")
    # Allow platform admin to also reach the Django admin site if needed.
    if not (platform_user.is_staff and platform_user.is_superuser):
        platform_user.is_staff = True
        platform_user.is_superuser = True
        platform_user.save()
    _make_user("admin@voiceofagirl.org", "Dr. Amina", "Okonjo", CustomUser.Role.ORGANISATION_ADMIN, org1)
    _make_user("manager@voiceofagirl.org", "Sarah", "Kibuuka", CustomUser.Role.PROGRAMME_MANAGER, org1)
    _make_user("mne@voiceofagirl.org", "Grace", "Namulindwa", CustomUser.Role.MONITORING_OFFICER, org1)
    _make_user("staff@voiceofagirl.org", "Peter", "Mugisha", CustomUser.Role.STAFF, org1)
    _make_user("admin@brightfutures.org", "Joyce", "Achieng", CustomUser.Role.ORGANISATION_ADMIN, org2)
    return org1, org2


def _create_programmes(org):
    from apps.programmes.models import Programme

    p1, _ = Programme.objects.get_or_create(
        organisation=org,
        name="Girls Education Initiative",
        defaults={
            "description": (
                "Improves school retention, attendance and learning outcomes for "
                "adolescent girls through scholarships, safe transport, mentoring "
                "and after-school learning support."
            ),
            "category": "Education",
            "location": "Kampala & Wakiso",
            "start_date": date(2026, 1, 10),
            "end_date": date(2026, 12, 15),
            "status": "ACTIVE",
            "target_participants": 150,
        },
    )
    p2, _ = Programme.objects.get_or_create(
        organisation=org,
        name="Digital Skills for Girls",
        defaults={
            "description": (
                "Practical digital literacy, online safety and coding-basics "
                "training delivered over 12 weeks in community technology hubs."
            ),
            "category": "Digital Skills",
            "location": "Kampala, Jinja & Gulu",
            "start_date": date(2026, 2, 1),
            "end_date": date(2026, 11, 30),
            "status": "ACTIVE",
            "target_participants": 120,
        },
    )
    p3, _ = Programme.objects.get_or_create(
        organisation=org,
        name="Mentorship & Leadership Circle",
        defaults={
            "description": (
                "A completed 2025 mentorship cohort that pairs girls with female "
                "professionals; used to demonstrate endline comparisons."
            ),
            "category": "Leadership",
            "location": "Kampala",
            "start_date": date(2025, 3, 1),
            "end_date": date(2025, 11, 30),
            "status": "COMPLETED",
            "target_participants": 60,
        },
    )
    return p1, p2, p3


def _create_org2_programme(org):
    from apps.programmes.models import Programme

    Programme.objects.get_or_create(
        organisation=org,
        name="Youth Employment Accelerator",
        defaults={
            "description": "Short vocational and job-readiness courses for young people in Mukono district.",
            "category": "Employment",
            "location": "Mukono",
            "start_date": date(2026, 4, 1),
            "end_date": date(2026, 10, 31),
            "status": "ACTIVE",
            "target_participants": 80,
        },
    )


def _create_participants(org, p1, p2, p3):
    """Seed 24 realistic participants across the three programmes."""
    from apps.participants.models import Participant

    random.seed(2026)
    names_p1 = [
        "Aisha Nakato", "Brenda Kirabo", "Christine Aber", "Doreen Namusoke",
        "Esther Atim", "Fatuma Nansubuga", "Grace Apio", "Hellen Nabwire",
        "Jackline Akello", "Kemia Namara", "Lydia Nakimuli", "Miriam Auma",
    ]
    names_p2 = [
        "Nancy Kembabazi", "Prossy Nalwoga", "Rehema Babirye", "Sharon Atuhaire",
        "Teddy Najjemba", "Umara Nalubega", "Vivian Aine", "Winnie Alanyo",
    ]
    names_p3 = [
        "Yvonne Namutebi", "Zainab Nabbosa", "Agnes Amongin", "Betty Adong",
    ]
    locations = ["Bugolobi", "Nakawa", "Katwe", "Bwaise", "Kireka", "Nansana", "Kasangati"]

    def _mk(programme, name, idx, status, age, gender="FEMALE"):
        first, last = name.split()[0].lower(), name.split()[1].lower()
        participant, _ = Participant.objects.get_or_create(
            organisation=org,
            name=name,
            defaults={
                "programme": programme,
                "email": f"{first}.{last}@example.org",
                "phone": f"+256 7{random.randint(70, 79)} {random.randint(100000, 999999)}",
                "external_reference": f"VOG-{programme.name.split()[0][:3].upper()}-{idx:03d}",
                "gender": gender,
                "age": age,
                "date_of_birth": date(2026 - age, random.randint(1, 12), random.randint(1, 28)),
                "location": random.choice(locations),
                "district": random.choice(["Kampala", "Wakiso", "Jinja", "Gulu"]),
                "status": status,
                "enrolled_date": programme.start_date + timedelta(days=random.randint(0, 30)),
            },
        )
        return participant

    participants = []
    for i, name in enumerate(names_p1):
        if i < 10:
            status = Participant.Status.ACTIVE
        elif i < 11:
            status = Participant.Status.COMPLETED
        else:
            status = Participant.Status.REGISTERED
        participants.append(_mk(p1, name, i + 1, status, random.randint(13, 19)))

    for i, name in enumerate(names_p2):
        gender = "MALE" if name == "Winnie Alanyo" else "FEMALE"
        status = Participant.Status.DROPPED_OUT if name == "Winnie Alanyo" else Participant.Status.ACTIVE
        participants.append(_mk(p2, name, i + 1, status, random.randint(16, 22), gender))

    for i, name in enumerate(names_p3):
        participants.append(_mk(p3, name, i + 1, Participant.Status.COMPLETED, random.randint(15, 20)))

    return participants


def _create_participants_org2(org):
    """Seed participants for the second organisation (tenant-isolation demo)."""
    from apps.participants.models import Participant
    from apps.programmes.models import Programme

    programme = Programme.objects.filter(organisation=org, name="Youth Employment Accelerator").first()
    names = [
        "Daniel Ssemakula", "Patricia Nyakato", "Ronald Opio",
        "Stella Nakabugo", "Brian Wandera", "Vicky Achan",
    ]
    participants = []
    for i, name in enumerate(names):
        participant, _ = Participant.objects.get_or_create(
            organisation=org,
            name=name,
            defaults={
                "programme": programme,
                "email": f"{name.split()[0].lower()}.{name.split()[1].lower()}@example.org",
                "phone": f"+256 7{random.randint(70, 79)} {random.randint(100000, 999999)}",
                "external_reference": f"BFY-{i + 1:03d}",
                "gender": "FEMALE" if i % 2 == 0 else "MALE",
                "age": random.randint(18, 24),
                "district": "Mukono",
                "status": Participant.Status.ACTIVE,
                "enrolled_date": date(2026, 4, random.randint(1, 28)),
            },
        )
        participants.append(participant)
    return participants


def _mk_survey(org, programme, title, stage, status, questions, start=None, end=None, impact_project=None):
    """Create a survey with its ordered question set (idempotent)."""
    from apps.surveys.models import Survey, SurveyQuestion

    survey, _ = Survey.objects.get_or_create(
        organisation=org,
        title=title,
        defaults={
            "programme": programme,
            "impact_project": impact_project,
            "description": (
                f"{title} — shared through a secure public link. "
                "No account is needed to respond."
            ),
            "stage": stage,
            "status": status,
            "start_date": start,
            "end_date": end,
            "thank_you_message": "Thank you! Your answer helps us improve the programme.",
        },
    )
    if not survey.questions.exists():
        for order, (text, qtype, options, required) in enumerate(questions, start=1):
            SurveyQuestion.objects.create(
                survey=survey,
                question=text,
                question_type=qtype,
                options=options,
                required=required,
                order=order,
            )
    return survey


def _create_surveys(org, p1, p2):
    from apps.surveys.models import Survey
    from django.utils import timezone

    now = timezone.now()
    baseline = _mk_survey(
        org, p1, "Baseline Survey", Survey.Stage.BASELINE, Survey.Status.PUBLISHED,
        start=now - timedelta(days=220),
        questions=[
            ("How old are you?", "NUMBER", [], True),
            ("Which district do you live in?", "DROPDOWN", ["Kampala", "Wakiso", "Jinja", "Gulu"], True),
            ("How often did you attend school last term?", "MULTIPLE_CHOICE",
             ["Every day", "Most days", "Some days", "Rarely"], True),
            ("How confident do you feel about your schoolwork? (1 = not at all, 5 = very)",
             "RATING_SCALE", [], True),
            ("Which challenges affect your education most?", "CHECKBOX",
             ["Transport costs", "School fees", "Menstrual health", "Family responsibilities",
              "Safety concerns", "Long distance to school"], False),
            ("Is there anything else you would like to tell us?", "LONG_TEXT", [], False),
        ],
    )
    midline = _mk_survey(
        org, p1, "Midline Monitoring Survey", Survey.Stage.MIDLINE, Survey.Status.PUBLISHED,
        start=now - timedelta(days=120),
        questions=[
            ("How often have you attended school this term?", "MULTIPLE_CHOICE",
             ["Every day", "Most days", "Some days", "Rarely"], True),
            ("How confident do you feel about your schoolwork now?", "RATING_SCALE", [], True),
            ("Which challenges are you still facing?", "CHECKBOX",
             ["Transport costs", "School fees", "Menstrual health", "Family responsibilities",
              "Safety concerns", "Long distance to school"], False),
            ("What has helped you most so far?", "SHORT_TEXT", [], True),
        ],
    )
    endline = _mk_survey(
        org, p1, "Endline Survey", Survey.Stage.ENDLINE, Survey.Status.PUBLISHED,
        start=now - timedelta(days=60),
        questions=[
            ("How often did you attend school this term?", "MULTIPLE_CHOICE",
             ["Every day", "Most days", "Some days", "Rarely"], True),
            ("How confident do you feel about your schoolwork at the end of the programme?",
             "RATING_SCALE", [], True),
            ("Would you recommend this programme to a friend?", "YES_NO", [], True),
            ("Please share a short story about your journey.", "LONG_TEXT", [], False),
        ],
    )
    feedback = _mk_survey(
        org, p1, "Participant Feedback Survey", Survey.Stage.CUSTOM, Survey.Status.PUBLISHED,
        start=now - timedelta(days=90),
        questions=[
            ("How satisfied are you with the programme overall?", "RATING_SCALE", [], True),
            ("Did you receive the support you needed?", "YES_NO", [], True),
            ("What could we improve?", "CHECKBOX",
             ["Communication", "Session times", "Venue", "Materials", "Mentoring", "Nothing"], False),
            ("Any other suggestions?", "LONG_TEXT", [], False),
        ],
    )
    digital = _mk_survey(
        org, p2, "Digital Skills Feedback Survey", Survey.Stage.CUSTOM, Survey.Status.PUBLISHED,
        start=now - timedelta(days=100),
        questions=[
            ("Do you feel more confident using a computer after the training?", "YES_NO", [], True),
            ("How would you rate your digital skills now? (1-5)", "RATING_SCALE", [], True),
            ("Which topic did you enjoy most?", "DROPDOWN",
             ["Typing", "Internet safety", "Email", "Coding basics", "Spreadsheets"], True),
            ("Comments about the training:", "LONG_TEXT", [], False),
        ],
    )
    # A closed survey so the demo can show the "survey closed" experience.
    _mk_survey(
        org, p1, "2025 Intake Survey (Archived)", Survey.Stage.BASELINE, Survey.Status.CLOSED,
        start=now - timedelta(days=400), end=now - timedelta(days=300),
        questions=[
            ("What is your name?", "SHORT_TEXT", [], True),
            ("Why did you join the programme?", "MULTIPLE_CHOICE",
             ["Learn new skills", "Meet mentors", "Improve grades", "Other"], True),
        ],
    )
    return {
        "baseline": baseline,
        "midline": midline,
        "endline": endline,
        "feedback": feedback,
        "digital": digital,
    }


def _create_responses(participants, surveys):
    """Generate realistic responses with backdated submission timestamps."""
    from apps.surveys.models import SurveyAnswer, SurveyResponse
    from django.utils import timezone

    random.seed(7)
    created = []

    def _submit(survey, participant, when, answers):
        answers = {q: v for q, v in answers.items() if v not in ("", None, [])}
        response = SurveyResponse.objects.create(
            survey=survey,
            organisation=survey.organisation,
            programme=survey.programme,
            participant=participant,
            respondent_name=participant.name if participant else "",
            metadata={"source": "public_link"},
        )
        SurveyResponse.objects.filter(pk=response.pk).update(submitted_at=when)
        SurveyAnswer.objects.bulk_create(
            [SurveyAnswer(response=response, question=q, value=v) for q, v in answers.items()]
        )
        created.append(response)
        return response

    def _q(survey):
        return {q.order: q for q in survey.questions.all()}

    baseline, midline, endline = surveys["baseline"], surveys["midline"], surveys["endline"]
    feedback, digital = surveys["feedback"], surveys["digital"]

    p1_rows = [p for p in participants if p.programme_id == baseline.programme_id]
    p2_rows = [p for p in participants if p.programme_id == digital.programme_id]
    challenges = ["Transport costs", "School fees", "Menstrual health",
                  "Family responsibilities", "Safety concerns", "Long distance to school"]

    # Baseline — every participant in programme one.
    qb = _q(baseline)
    for i, p in enumerate(p1_rows):
        when = timezone.make_aware(datetime(2026, 2, 3)) + timedelta(
            days=i * 4, hours=random.randint(7, 19)
        )
        _submit(baseline, p, when, {
            qb[1]: p.age or 15,
            qb[2]: p.district if p.district in ["Kampala", "Wakiso", "Jinja", "Gulu"] else "Kampala",
            qb[3]: random.choice(["Some days", "Rarely", "Most days"]),
            qb[4]: random.randint(1, 3),
            qb[5]: random.sample(challenges, k=random.randint(1, 3)),
        })

    # Midline — 9 of 12, showing improvement.
    qm = _q(midline)
    for i, p in enumerate(p1_rows[:9]):
        when = timezone.make_aware(datetime(2026, 4, 10)) + timedelta(
            days=i * 2, hours=random.randint(7, 19)
        )
        _submit(midline, p, when, {
            qm[1]: random.choice(["Most days", "Every day"]),
            qm[2]: random.randint(3, 4),
            qm[3]: random.sample(challenges, k=random.randint(0, 2)),
            qm[4]: random.choice([
                "The mentor check-ins", "Learning materials", "My teachers",
                "The safe space sessions", "Support from my family",
            ]),
        })

    # Endline — 6 of 12, strong outcomes for baseline/endline comparison.
    qe = _q(endline)
    for i, p in enumerate(p1_rows[:6]):
        when = timezone.make_aware(datetime(2026, 6, 5)) + timedelta(
            days=i * 3, hours=random.randint(7, 19)
        )
        _submit(endline, p, when, {
            qe[1]: random.choice(["Every day", "Most days"]),
            qe[2]: random.randint(4, 5),
            qe[3]: True,
            qe[4]: "I believe in myself now. I want to finish school and become a leader.",
        })

    # Anonymous walk-in responses captured through the public link (no participant).
    for i in range(4):
        when = timezone.make_aware(datetime(2026, 3, 1)) + timedelta(
            days=i * 5, hours=random.randint(7, 19)
        )
        _submit(baseline, None, when, {
            qb[1]: random.randint(13, 18),
            qb[2]: random.choice(["Kampala", "Wakiso"]),
            qb[3]: random.choice(["Some days", "Most days"]),
            qb[4]: random.randint(2, 3),
            qb[5]: random.sample(challenges, k=2),
        })

    # Participant feedback survey.
    qf = _q(feedback)
    for i, p in enumerate(p1_rows[:8]):
        when = timezone.make_aware(datetime(2026, 5, 4)) + timedelta(
            days=i * 2, hours=random.randint(7, 19)
        )
        _submit(feedback, p, when, {
            qf[1]: random.randint(3, 5),
            qf[2]: i % 4 != 3,
            qf[3]: random.sample(
                ["Communication", "Session times", "Venue", "Materials", "Mentoring", "Nothing"],
                k=random.randint(0, 2),
            ),
        })

    # Digital skills survey for programme two.
    qd = _q(digital)
    for i, p in enumerate(p2_rows[:7]):
        when = timezone.make_aware(datetime(2026, 5, 12)) + timedelta(
            days=i * 2, hours=random.randint(7, 19)
        )
        _submit(digital, p, when, {
            qd[1]: i != 3,
            qd[2]: random.randint(3, 5),
            qd[3]: random.choice(["Typing", "Internet safety", "Email", "Coding basics", "Spreadsheets"]),
        })

    return created


def _create_org2_surveys(org):
    """Give organisation B its own survey and responses (tenant isolation demo)."""
    from apps.participants.models import Participant
    from apps.surveys.models import Survey, SurveyAnswer, SurveyResponse
    from django.utils import timezone

    survey = _mk_survey(
        org, None, "Intake Survey", Survey.Stage.BASELINE, Survey.Status.PUBLISHED,
        start=timezone.now() - timedelta(days=60),
        questions=[
            ("What is your age?", "NUMBER", [], True),
            ("What is your highest level of education?", "DROPDOWN",
             ["Primary", "O-Level", "A-Level", "Vocational"], True),
            ("Are you currently employed?", "YES_NO", [], True),
        ],
    )
    q_age = survey.questions.order_by("order").first()
    q_edu = survey.questions.order_by("order").all()[1]
    for i, p in enumerate(Participant.objects.filter(organisation=org)[:4]):
        response = SurveyResponse.objects.create(
            survey=survey,
            organisation=org,
            programme=survey.programme,
            participant=p,
            respondent_name=p.name,
            metadata={"source": "public_link"},
        )
        SurveyResponse.objects.filter(pk=response.pk).update(
            submitted_at=timezone.make_aware(datetime(2026, 5, 2)) + timedelta(days=i)
        )
        SurveyAnswer.objects.bulk_create([
            SurveyAnswer(response=response, question=q_age, value=p.age or 20),
            SurveyAnswer(response=response, question=q_edu,
                         value=random.choice(["Primary", "O-Level", "A-Level", "Vocational"])),
        ])


def _create_kpis(org, p1, p2):
    """Seed the four headline KPIs with baseline / current / target / endline."""
    from apps.impact.models import KPI

    def _kpi(programme, name, description, baseline, current, target,
             endline=None, status=None):
        kpi, _ = KPI.objects.get_or_create(
            organisation=org,
            programme=programme,
            name=name,
            defaults={
                "description": description,
                "unit": "%",
                "baseline": baseline,
                "current_value": current,
                "target": target,
                "endline": endline,
                "status": status or KPI.Status.ON_TRACK,
            },
        )
        return kpi

    k1 = _kpi(
        p1, "School attendance",
        "Share of participants attending school at least most days of the term.",
        62.0, 74.0, 85.0, endline=81.0,
    )
    k2 = _kpi(
        p1, "Programme completion",
        "Participants who complete all programme sessions and graduate.",
        None, 76.0, 85.0,
    )
    k3 = _kpi(
        p1, "Leadership confidence",
        "Participants reporting improved leadership confidence in surveys.",
        48.0, 59.0, 75.0, status=KPI.Status.AT_RISK,
    )
    k4 = _kpi(
        p2, "Digital skills confidence",
        "Participants confident using a computer for school or work.",
        41.0, 66.0, 80.0, endline=72.0,
    )
    return [k1, k2, k3, k4]


def _create_measurements(org, p1, kpis):
    """Monthly impact-measurement time series powering trend charts."""
    from apps.impact.models import ImpactMeasurement

    months = [(2026, m) for m in range(1, 10)]
    for kpi in kpis:
        start = kpi.baseline if kpi.baseline is not None else kpi.current_value * 0.5
        for i, (year, month) in enumerate(months):
            value = start + (kpi.current_value - start) * i / (len(months) - 1)
            ImpactMeasurement.objects.get_or_create(
                organisation=org, kpi=kpi, metric=kpi.name, period=date(year, month, 1),
                defaults={"value": round(value, 1), "programme": kpi.programme},
            )
    # Enrolment growth series used by the overview trend chart.
    for i, (year, month) in enumerate(months):
        ImpactMeasurement.objects.get_or_create(
            organisation=org, metric="Participants enrolled", period=date(year, month, 1),
            defaults={"value": 40 + i * 22, "programme": p1, "notes": "Cumulative enrolment."},
        )


def _create_monitoring(org, p1, p2):
    """Seed challenges, feedback and support requests with realistic statuses."""
    from apps.accounts.models import CustomUser
    from apps.monitoring.models import Challenge, Feedback, SupportRequest
    from django.utils import timezone

    manager = CustomUser.objects.filter(organisation=org, role=CustomUser.Role.PROGRAMME_MANAGER).first()
    mne = CustomUser.objects.filter(organisation=org, role=CustomUser.Role.MONITORING_OFFICER).first()
    now = timezone.now()

    challenges = [
        (p1, "TRANSPORT", "Bus fare increase on Kampala road",
         "Fuel prices raised boda and bus fares for girls commuting from Nansana.",
         "HIGH", "IN_PROGRESS", manager, None),
        (p1, "ATTENDANCE", "Recurring absence — Kemia Namara",
         "Missed six sessions in April; family is moving houses.",
         "HIGH", "RESOLVED", mne, 20),
        (p1, "EQUIPMENT", "Shortage of exercise books",
         "Twelve girls lack books after the mid-term distribution.",
         "MEDIUM", "OPEN", None, None),
        (p2, "EQUIPMENT", "Community hub computers ageing",
         "Three of ten desktops need replacement before the next cohort.",
         "HIGH", "IN_PROGRESS", manager, None),
        (p1, "SCHEDULING", "Mentor session clashes with exams",
         "Sessions overlap the national examination week.",
         "MEDIUM", "OPEN", None, None),
        (p1, "SAFETY", "Unsafe walkway after dusk sessions",
         "Girls walk home alone late on Wednesdays.",
         "CRITICAL", "IN_PROGRESS", manager, None),
        (p2, "FINANCIAL", "Transport stipends exhausted",
         "The budget for participant travel stipends ran out early.",
         "HIGH", "OPEN", None, None),
        (p1, "FAMILY_CARE", "Care duties during planting season",
         "Two participants are needed at home for family farming.",
         "LOW", "OPEN", None, None),
        (p1, "HEALTH", "Malaria outbreak in Bwaise",
         "Several participants were sick during the same week.",
         "MEDIUM", "RESOLVED", mne, 12),
        (p2, "ATTENDANCE", "Low Friday turnout in Gulu hub",
         "Attendance dips to about 60% on Fridays.",
         "MEDIUM", "RESOLVED", manager, 8),
        (p1, "TRANSPORT", "Bicycle programme delayed",
         "The bike donation is pending customs clearance.",
         "LOW", "OPEN", None, None),
        (p1, "OTHER", "Data collection training needed",
         "Field staff need a refresher on the survey workflow.",
         "MEDIUM", "RESOLVED", mne, 5),
    ]
    for programme, category, title, description, priority, status, assigned, resolved in challenges:
        defaults = {
            "programme": programme,
            "category": category,
            "description": description,
            "priority": priority,
            "status": status,
            "assigned_to": assigned,
        }
        if resolved is not None:
            defaults["resolved_at"] = now - timedelta(days=resolved)
            defaults["resolution_notes"] = (
                "Resolved with the family and school. Follow-up visit scheduled."
            )
        Challenge.objects.get_or_create(organisation=org, title=title, defaults=defaults)

    feedback_items = [
        (p1, "PROGRAMME", "The mentoring sessions helped me speak up in class.", "ACTIONED"),
        (p1, "MATERIALS", "We need more practice books for mathematics.", "NEW"),
        (p1, "FACILITATOR", "Our facilitator explains every topic clearly.", "REVIEWED"),
        (p2, "PROGRAMME", "Can we have weekend classes for those in school?", "NEW"),
        (p1, "VENUE", "The hall is too hot in the afternoon.", "REVIEWED"),
        (p2, "GENERAL", "Thank you for the graduation certificates!", "ACTIONED"),
    ]
    for programme, category, message, status in feedback_items:
        Feedback.objects.get_or_create(
            organisation=org, message=message,
            defaults={"programme": programme, "category": category, "status": status},
        )

    support_items = [
        (p1, "TRAINING", "Refresher training for new mentors", "IN_PROGRESS", manager, None),
        (p2, "TECHNICAL", "Cannot upload attendance sheet from a phone", "OPEN", None, None),
        (p1, "MATERIALS", "Request a projector for the Kampala hub", "OPEN", None, None),
        (p1, "DATA", "Fix duplicate participant records", "RESOLVED", mne, 10),
        (p2, "OTHER", "Help setting up the endline survey", "IN_PROGRESS", mne, None),
    ]
    for programme, category, description, status, assigned, resolved in support_items:
        defaults = {
            "programme": programme,
            "category": category,
            "status": status,
            "assigned_to": assigned,
        }
        if resolved is not None:
            defaults["resolved_at"] = now - timedelta(days=resolved)
            defaults["resolution_notes"] = "Records merged and validation added."
        SupportRequest.objects.get_or_create(
            organisation=org, description=description, defaults=defaults,
        )


def _create_impact_project(org):
    """Standalone impact project: own KPI, survey, public responses and trends."""
    from apps.accounts.models import CustomUser
    from apps.impact.models import ImpactMeasurement, ImpactProject, KPI
    from apps.surveys.models import Survey, SurveyAnswer, SurveyResponse
    from django.utils import timezone

    admin = CustomUser.objects.filter(organisation=org, role=CustomUser.Role.ORGANISATION_ADMIN).first()
    project, _ = ImpactProject.objects.get_or_create(
        organisation=org,
        name="Community Awareness Campaign 2026",
        defaults={
            "description": (
                "A standalone impact project measuring community awareness of girls' "
                "education rights across three districts. It runs independently of the "
                "full programme-management tools."
            ),
            "status": ImpactProject.Status.ACTIVE,
            "start_date": date(2026, 3, 1),
            "end_date": date(2026, 9, 30),
            "created_by": admin,
        },
    )
    kpi, _ = KPI.objects.get_or_create(
        organisation=org,
        impact_project=project,
        name="Community awareness of girls' education rights",
        defaults={
            "unit": "%",
            "baseline": 30.0,
            "current_value": 55.0,
            "target": 70.0,
            "status": KPI.Status.ON_TRACK,
        },
    )
    survey = _mk_survey(
        org, None, "Community Needs Snapshot", Survey.Stage.CUSTOM, Survey.Status.PUBLISHED,
        start=timezone.now() - timedelta(days=45), impact_project=project,
        questions=[
            ("Which community do you live in?", "DROPDOWN", ["Kampala", "Wakiso", "Mukono"], True),
            ("Before this campaign, did you know girls have a legal right to education?",
             "YES_NO", [], True),
            ("How likely are you to support a girl's education after this campaign? (1-5)",
             "RATING_SCALE", [], True),
            ("What message stuck with you most?", "SHORT_TEXT", [], True),
        ],
    )
    random.seed(11)
    q1, q2, q3, q4 = list(survey.questions.order_by("order"))
    for i in range(12):
        when = timezone.make_aware(datetime(2026, 7, 3)) + timedelta(
            days=i * 2, hours=random.randint(8, 18)
        )
        response = SurveyResponse.objects.create(
            survey=survey,
            organisation=org,
            programme=None,
            participant=None,
            impact_project=project,
            respondent_name=random.choice(["", "Community volunteer", "Local leader", "Parent"]),
            metadata={"source": "public_link"},
        )
        SurveyResponse.objects.filter(pk=response.pk).update(submitted_at=when)
        SurveyAnswer.objects.bulk_create([
            SurveyAnswer(response=response, question=q1,
                         value=random.choice(["Kampala", "Wakiso", "Mukono"])),
            SurveyAnswer(response=response, question=q2, value=i > 2),
            SurveyAnswer(response=response, question=q3, value=random.randint(3, 5)),
            SurveyAnswer(response=response, question=q4, value=random.choice([
                "Every girl deserves a classroom", "Education changes families",
                "Keep girls in school", "Support her dream",
            ])),
        ])
    for i, month in enumerate(range(3, 10)):
        ImpactMeasurement.objects.get_or_create(
            organisation=org, kpi=kpi, metric=kpi.name, impact_project=project,
            period=date(2026, month, 1),
            defaults={"value": round(30 + (55 - 30) * i / 6, 1)},
        )
    return project