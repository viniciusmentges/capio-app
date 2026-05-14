from django.db import transaction
from apps.users.models import UserFeedback
from apps.bible.models import PassageExplanation
from apps.devotional.models import DevotionalContent
from apps.reflection.models import DailyReflection
from services.exceptions import NotFoundException

class FeedbackService:
    @classmethod
    @transaction.atomic
    def submit(cls, user, response_type: str, content_ref_id: int, helpful: bool, comment: str = ""):
        # Validate existence
        if response_type == 'BIBLE':
            exists = PassageExplanation.objects.filter(id=content_ref_id).exists()
        elif response_type == 'DEVOTIONAL':
            exists = DevotionalContent.objects.filter(id=content_ref_id).exists()
        elif response_type == 'REFLECTION':
            exists = DailyReflection.objects.filter(id=content_ref_id).exists()
        else:
            raise ValueError(f"Invalid response_type: {response_type}")

        if not exists:
            raise NotFoundException(f"{response_type} with id {content_ref_id} not found.")

        feedback, created = UserFeedback.objects.update_or_create(
            user=user,
            response_type=response_type,
            content_ref_id=content_ref_id,
            defaults={
                'helpful': helpful,
                'comment': comment
            }
        )

        return {
            "id": feedback.id,
            "response_type": feedback.response_type,
            "content_ref_id": feedback.content_ref_id,
            "helpful": feedback.helpful,
            "comment": feedback.comment,
            "created": created
        }
