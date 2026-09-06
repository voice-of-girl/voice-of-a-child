"""
Public survey endpoints.

No authentication required. Token-based access via cryptographically secure
public_token. Protections: honeypot, rate limiting, strict answer validation,
duplicate-submission guards, and expiry/closure enforcement.
"""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.participants.models import Participant

from .models import Survey, SurveyResponse
from .serializers import PublicResponseSerializer, PublicSurveySerializer
from .services import store_response, validate_answers


class PublicSurveyView(APIView):
    """GET /api/public/surveys/{public_token}/ — fetch the public survey."""

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_survey"

    def get(self, request, public_token):
        survey = Survey.objects.select_related("organisation").prefetch_related(
            "questions"
        ).filter(public_token=public_token).first()
        if survey is None:
            return Response(
                {"detail": "Survey not found.", "status": "NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = PublicSurveySerializer(survey).data
        data["accepting_responses"] = survey.is_accepting_responses()
        if not data["accepting_responses"]:
            data["message"] = (
                "This survey is currently closed or not yet open."
                if survey.status != Survey.Status.CLOSED
                else "This survey has been closed."
            )
        return Response(data)


class PublicSurveySubmitView(APIView):
    """
    POST /api/public/surveys/{public_token}/responses/

    Accepts an anonymous response. Validates server-side, associates the
    response with the correct organisation, programme, survey and (when an
    email match is found) participant.
    """

    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_submit"

    def post(self, request, public_token):
        survey = Survey.objects.select_related("organisation").filter(
            public_token=public_token
        ).first()
        if survey is None:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not survey.is_accepting_responses():
            reason = (
                "closed"
                if survey.status == Survey.Status.CLOSED
                else "not yet open or expired"
            )
            return Response(
                {"detail": f"This survey is {reason} and no longer accepts responses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PublicResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Honeypot: silently accept bot submissions without persisting.
        if data.get("website"):
            return Response(
                {"detail": "Thank you for your response.", "accepted": True}, status=201
            )

        # Validate answers against the survey schema.
        errors, clean_answers = validate_answers(survey, data.get("answers", {}))
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        email = (data.get("respondent_email") or "").strip().lower()
        participant = None
        if email:
            participant = (
                Participant.objects.filter(
                    organisation=survey.organisation, email__iexact=email
                )
                .order_by("-created_at")
                .first()
            )

        # Duplicate submission guard.
        if not survey.allow_multiple_responses:
            duplicate = None
            if participant is not None:
                duplicate = SurveyResponse.objects.filter(
                    survey=survey, participant=participant
                ).exists()
            elif email:
                duplicate = SurveyResponse.objects.filter(
                    survey=survey, respondent_email__iexact=email
                ).exists()
            if duplicate:
                return Response(
                    {
                        "detail": (
                            "A response for this survey has already been recorded "
                            "for this person. Only one response is allowed."
                        )
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        response = store_response(
            survey,
            organisation=survey.organisation,
            answers=clean_answers,
            participant=participant,
            respondent_name=data.get("respondent_name", ""),
            respondent_email=email,
            metadata={
                "via": "public_link",
            },
        )
        return Response(
            {
                "detail": "Thank you for your response.",
                "accepted": True,
                "response_id": str(response.id),
                "participant_matched": participant is not None,
            },
            status=status.HTTP_201_CREATED,
        )