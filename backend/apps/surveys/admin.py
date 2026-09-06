from django.contrib import admin

from .models import Survey, SurveyAnswer, SurveyQuestion, SurveyResponse


class QuestionInline(admin.TabularInline):
    model = SurveyQuestion
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title", "organisation", "programme", "stage", "status")
    list_filter = ("status", "stage", "organisation")
    search_fields = ("title", "organisation__name")
    inlines = [QuestionInline]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("survey", "organisation", "submitted_at")
    list_filter = ("organisation", "survey")


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ("response", "question", "value")


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ("survey", "order", "question_type", "required")
    list_filter = ("question_type",)