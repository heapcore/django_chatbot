import logging
import uuid

from django.contrib.auth.models import Group, User
from rest_framework import status, viewsets, views
from rest_framework.response import Response

from back.serializers import (
    GroupSerializer,
    QuestionnaireImportSerializer,
    QuestionnaireSerializer,
    UserSerializer,
)
from questionnaire.models import (
    HistoryQuestionAnswer,
    QuestionAnswerRelation,
    Questionnaire,
    QuestionnaireImport,
)

logger = logging.getLogger(__name__)


def _serialize_question(question):
    relations = QuestionAnswerRelation.objects.filter(
        question_from_id=question.id
    ).order_by("id")
    return {
        "id": question.id,
        "text": question.name,
        "answers": [rel.condition for rel in relations],
        "is_leaf": question.is_leaf,
    }


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer


class QuestionnaireImportViewSet(viewsets.ModelViewSet):
    queryset = QuestionnaireImport.objects.all()
    serializer_class = QuestionnaireImportSerializer


class ChatQuestionnaireList(views.APIView):
    def get(self, request):
        items = Questionnaire.objects.all().order_by("id").values("id", "name")
        return Response(list(items), status=status.HTTP_200_OK)


class ChatStart(views.APIView):
    def post(self, request):
        questionnaire_id = request.data.get("questionnaire_id")
        if questionnaire_id is None:
            return Response(
                {"detail": 'Field "questionnaire_id" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            questionnaire = Questionnaire.objects.select_related(
                "start_question_id"
            ).get(id=questionnaire_id)
        except Questionnaire.DoesNotExist:
            return Response(
                {"detail": "Questionnaire not found."}, status=status.HTTP_404_NOT_FOUND
            )

        session_id = request.data.get("session_id") or str(uuid.uuid4())
        HistoryQuestionAnswer.objects.filter(uuid=session_id).delete()

        question_payload = _serialize_question(questionnaire.start_question_id)
        return Response(
            {
                "session_id": session_id,
                "questionnaire": {"id": questionnaire.id, "name": questionnaire.name},
                "question": question_payload,
                "completed": question_payload["is_leaf"],
            },
            status=status.HTTP_200_OK,
        )


class ChatAnswer(views.APIView):
    def post(self, request):
        session_id = request.data.get("session_id")
        question_id = request.data.get("question_id")
        answer = request.data.get("answer")

        if not session_id:
            return Response(
                {"detail": 'Field "session_id" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if question_id is None:
            return Response(
                {"detail": 'Field "question_id" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(answer, str) or not answer.strip():
            return Response(
                {"detail": 'Field "answer" must be a non-empty string.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answer = answer.strip()
        relation = (
            QuestionAnswerRelation.objects.select_related(
                "question_from_id", "question_to_id"
            )
            .filter(question_from_id=question_id, condition__iexact=answer)
            .first()
        )

        if relation is None:
            available_answers = list(
                QuestionAnswerRelation.objects.filter(
                    question_from_id=question_id
                ).values_list("condition", flat=True)
            )
            return Response(
                {
                    "detail": "No transition found for this answer.",
                    "available_answers": available_answers,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        HistoryQuestionAnswer.objects.create(
            question_id=relation.question_from_id,
            answer=answer,
            uuid=session_id,
        )

        next_question = relation.question_to_id
        payload = _serialize_question(next_question)
        completed = payload["is_leaf"]

        if completed:
            answers_history = HistoryQuestionAnswer.objects.filter(
                uuid=session_id
            ).order_by("date_create")
            if answers_history:
                history_text = (
                    "Answers history: " + answers_history[0].question_id.name + ": "
                )
                history_text += " -> ".join([item.answer for item in answers_history])
                logger.info(history_text)

        return Response(
            {
                "session_id": session_id,
                "question": payload,
                "completed": completed,
            },
            status=status.HTTP_200_OK,
        )
