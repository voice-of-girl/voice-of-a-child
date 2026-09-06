from django.utils import timezone
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.surveys.models import Answer, Survey, SurveyResponse
from apps.surveys.serializers import (
    PublicSurveySerializer,
    PublicSurveySubmitSerializer,
)


class PublicSurveyLinkView(views.APIView):
    """Participants complete surveys via a secure token link - no login needed."""

    permission_classes = [AllowAny]

    def get_object(self, token):
        response = (
            SurveyResponse.objects.select_related("survey", "participant")
            .filter(access_token=token)
            .first()
        )
        return response

    def get(self, request, token):
        response = self.get_object(token)
        if not response:
            return Response({"detail": "Invalid or expired survey link."}, status=status.HTTP_404_NOT_FOUND)
        if response.submitted:
            return Response(
                {"detail": "This survey has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if response.survey.status != Survey.Status.PUBLISHED:
            return Response(
                {"detail": "This survey is not currently open."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = PublicSurveySerializer(response.survey).data
        data["respondent"] = (
            {
                "id": response.participant.id,
                "full_name": response.participant.full_name,
            }
            if response.participant
            else None
        )
        data["response_id"] = response.id
        return Response(data)

    def post(self, request, token):
        response = self.get_object(token)
        if not response:
            return Response({"detail": "Invalid or expired survey link."}, status=status.HTTP_404_NOT_FOUND)
        if response.submitted:
            return Response(
                {"detail": "This survey has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if response.survey.status != Survey.Status.PUBLISHED:
            return Response(
                {"detail": "This survey is not currently open."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PublicSurveySubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data["answers"]

        questions = {q.id: q for q in response.survey.questions.all()}
        response.answers.all().delete()

        # Validate required answers and question types.
        for answer in answers:
            question = questions.get(answer["question_id"])
            if not question:
                return Response(
                    {"detail": f"Question {answer['question_id']} not found in this survey."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Answer.objects.create(
                response=response,
                question=question,
                value=answer["value"],
            )

        missing_required = [
            q.question_text
            for q in response.survey.questions.filter(required=True)
            if q.id not in {a["question_id"] for a in answers}
        ]
        if missing_required:
            response.answers.all().delete()
            return Response(
                {"detail": f"Missing required answers: {', '.join(missing_required)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response.submitted = True
        response.submitted_at = timezone.now()
        response.save()
        return Response(
            {
                "detail": "Response recorded. Thank you!",
                "response_id": response.id,
            },
            status=status.HTTP_201_CREATED,
        )