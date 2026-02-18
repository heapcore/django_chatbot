import json

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Questionnaire(models.Model):
    name = models.CharField(blank=False, unique=True, max_length=255)
    start_question_id = models.ForeignKey(
        "questionnaire.QuestionAnswer", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class QuestionnaireImport(models.Model):
    json_file = models.FileField(blank=False)
    status = models.TextField(blank=True, max_length=255)

    def __str__(self):
        return str(self.json_file)

    @staticmethod
    def process_import(instance):
        uploaded_file = instance.json_file
        raw_payload = uploaded_file.file.read()
        uploaded_file.file.seek(0)

        try:
            json_data = json.loads(raw_payload)
        except Exception:
            instance.status = "Invalid JSON payload"
            return

        if not isinstance(json_data, list):
            instance.status = "Invalid format: top-level JSON value must be a list"
            return

        messages = []

        for json_questionnaire in json_data:
            # Using special parser for saving questionnaire structure to database.
            from questionnaire.core.questionnaire_parser import QuestionnaireParser

            try:
                questionnaire = QuestionnaireParser(json_questionnaire)
                is_valid, message = questionnaire.validate()
                if is_valid:
                    questionnaire.save()
                else:
                    messages.append(message)
            except Exception as exc:
                messages.append("Cannot save questionnaire: {0}".format(str(exc)))

        instance.status = "; ".join(messages) if messages else "Ok"


class QuestionAnswer(models.Model):
    name = models.CharField(blank=False, max_length=255)
    is_leaf = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class HistoryQuestionAnswer(models.Model):
    question_id = models.ForeignKey(
        "questionnaire.QuestionAnswer",
        related_name="question",
        on_delete=models.CASCADE,
        blank=False,
    )
    answer = models.CharField(blank=False, max_length=255)
    date_create = models.DateTimeField(auto_now_add=True)
    uuid = models.CharField(blank=False, max_length=255)

    def __str__(self):
        return self.question_id.name + ": " + self.answer


class QuestionAnswerRelation(models.Model):
    question_from_id = models.ForeignKey(
        "questionnaire.QuestionAnswer",
        related_name="question_from",
        on_delete=models.CASCADE,
        blank=False,
    )
    question_to_id = models.ForeignKey(
        "questionnaire.QuestionAnswer",
        related_name="question_to",
        on_delete=models.CASCADE,
        blank=False,
    )
    condition = models.CharField(blank=False, max_length=255)

    def __str__(self):
        return "{question} ({condition}) -> {answer}".format(
            question=str(self.question_from_id),
            answer=str(self.question_to_id),
            condition=self.condition,
        )


@receiver(
    pre_save, sender=QuestionnaireImport, dispatch_uid="questionnaire_import_pre_save"
)
def questionnaire_import_pre_save(sender, instance, **kwargs):
    QuestionnaireImport.process_import(instance)
