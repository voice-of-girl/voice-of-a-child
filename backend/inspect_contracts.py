"""Dev helper: print model choices, auth/admin URL routes (frontend contract)."""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.urls import get_resolver  # noqa: E402

from apps.accounts.models import CustomUser  # noqa: E402
from apps.impact.models import ImpactProject, KPI  # noqa: E402
from apps.monitoring.models import Challenge, Feedback, SupportRequest  # noqa: E402
from apps.participants.models import Participant  # noqa: E402
from apps.programmes.models import Programme  # noqa: E402
from apps.reports.models import Report  # noqa: E402
from apps.surveys.models import Survey, SurveyQuestion  # noqa: E402

for m in [
    Survey,
    SurveyQuestion,
    Programme,
    Participant,
    Challenge,
    Feedback,
    SupportRequest,
    KPI,
    ImpactProject,
    Report,
    CustomUser,
]:
    for name in dir(m):
        attr = getattr(m, name)
        if isinstance(attr, type) and getattr(attr, "choices", None):
            print(f"{m.__name__}.{name}: {[c[0] for c in attr.choices]}")

print("---ROUTES---")


def walk(patterns, prefix=""):
    for p in patterns:
        if hasattr(p, "url_patterns"):
            walk(p.url_patterns, prefix + str(p.pattern))
        else:
            full = prefix + str(p.pattern)
            if full.startswith("api/admin") or full.startswith("api/auth"):
                print(full)


walk(get_resolver().url_patterns)
