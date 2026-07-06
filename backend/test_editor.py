import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
import django
django.setup()

from services.editorial.editor import EditorialEditorService

class EditorialEditorServiceTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.argv_patcher = patch.object(sys, 'argv', ['test_editor.py'])
        self.argv_patcher.start()

    def tearDown(self):
        self.argv_patcher.stop()
        super().tearDown()

    @patch('services.editorial.editor.get_ai_service')
    def test_review_and_publish_approved(self, mock_get_ai):
        mock_ai = MagicMock()
        mock_ai.evaluate_and_refine_editorial.return_value = {
            "scores": {
                "clareza": 9.5,
                "naturalidade": 9.5,
                "correcao_gramatical": 10.0,
                "aderencia_gramatica_silencio": 10.0
            },
            "aprovado": True,
            "texto_refinado": None
        }
        mock_get_ai.return_value = mock_ai

        draft = {
            "title": "O repouso real",
            "reflection": "Deus acolhe o cansado no silêncio da manhã."
        }

        result = EditorialEditorService.review_and_publish(draft)
        self.assertEqual(result["title"], "O repouso real")
        self.assertEqual(result["reflection"], "Deus acolhe o cansado no silêncio da manhã.")
        self.assertEqual(mock_ai.evaluate_and_refine_editorial.call_count, 1)

    @patch('services.editorial.editor.get_ai_service')
    def test_review_and_publish_refinement_cycle(self, mock_get_ai):
        mock_ai = MagicMock()
        # No primeiro ciclo, nota baixa de clareza (7.0) -> retorna texto refinado
        # No segundo ciclo, nota 9.5 -> aprova (>= 9.2)
        mock_ai.evaluate_and_refine_editorial.side_effect = [
            {
                "scores": {"clareza": 7.0, "naturalidade": 8.5, "correcao_gramatical": 9.0, "aderencia_gramatica_silencio": 9.0},
                "aprovado": False,
                "texto_refinado": {
                    "title": "O repouso claro",
                    "reflection": "Texto reescrito com clareza cristalina para quem está exausto."
                }
            },
            {
                "scores": {"clareza": 9.5, "naturalidade": 9.5, "correcao_gramatical": 10.0, "aderencia_gramatica_silencio": 10.0},
                "aprovado": True,
                "texto_refinado": None
            }
        ]
        mock_get_ai.return_value = mock_ai

        draft = {
            "title": "Abstração etérea apelo jornada",
            "reflection": "Cristo sentiu o apelo inteiro e permaneceu de pé na jornada condicional."
        }

        result = EditorialEditorService.review_and_publish(draft)
        self.assertEqual(result["title"], "O repouso claro")
        self.assertEqual(result["reflection"], "Texto reescrito com clareza cristalina para quem está exausto.")
        self.assertEqual(mock_ai.evaluate_and_refine_editorial.call_count, 2)

if __name__ == '__main__':
    unittest.main()
