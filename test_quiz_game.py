"""야구 규칙 퀴즈 게임 자동 테스트

실행: python test_quiz_game.py   (Mac은 python3)
- 실제 state.json은 건드리지 않도록 임시 폴더를 사용한다.
- 사용자 입력(input)은 unittest.mock으로 미리 정한 값을 넣는다.
"""
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import quiz_game
from quiz import Quiz
from quiz_game import QuizGame


def run_with_inputs(func, inputs):
    """input()에 inputs를 차례로 넣고, 화면 출력은 문자열로 돌려준다."""
    with patch("builtins.input", side_effect=inputs), \
            patch("sys.stdout", new_callable=io.StringIO) as out:
        func()
    return out.getvalue()


class TestQuiz(unittest.TestCase):
    """Quiz 클래스 테스트"""

    def setUp(self):
        self.quiz = Quiz("볼 4개면?", ["삼진", "볼넷", "홈런", "아웃"], 2)

    def test_is_correct(self):
        self.assertTrue(self.quiz.is_correct(2))
        self.assertFalse(self.quiz.is_correct(1))

    def test_to_dict_and_from_dict(self):
        restored = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(restored.question, self.quiz.question)
        self.assertEqual(restored.choices, self.quiz.choices)
        self.assertEqual(restored.answer, self.quiz.answer)

    def test_from_dict_rejects_wrong_choice_count(self):
        with self.assertRaises(ValueError):
            Quiz.from_dict({"question": "Q", "choices": ["a", "b"], "answer": 1})

    def test_from_dict_rejects_answer_out_of_range(self):
        with self.assertRaises(ValueError):
            Quiz.from_dict({"question": "Q", "choices": ["a", "b", "c", "d"], "answer": 5})


class GameTestBase(unittest.TestCase):
    """임시 폴더의 state.json을 쓰도록 바꿔치기하는 공통 준비"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state_path = os.path.join(self.tmp.name, "state.json")
        self.backup_path = self.state_path + ".bak"
        self.patchers = [
            patch.object(quiz_game, "STATE_FILE", self.state_path),
            patch.object(quiz_game, "BACKUP_FILE", self.backup_path),
        ]
        for p in self.patchers:
            p.start()

    def tearDown(self):
        for p in self.patchers:
            p.stop()
        self.tmp.cleanup()

    def make_game(self):
        with patch("sys.stdout", new_callable=io.StringIO):
            return QuizGame()


class TestInput(GameTestBase):
    """공통 입력/예외 처리 기준 테스트"""

    def test_strips_spaces(self):
        game = self.make_game()
        with patch("builtins.input", side_effect=["  3  "]):
            self.assertEqual(game.input_number("> ", 1, 5), 3)

    def test_retries_on_text_empty_and_out_of_range(self):
        game = self.make_game()
        result = {}
        out = run_with_inputs(
            lambda: result.setdefault("n", game.input_number("> ", 1, 5)),
            ["abc", "", "9", "0", "2"],
        )
        self.assertEqual(result["n"], 2)
        self.assertIn("숫자만 입력해 주세요", out)
        self.assertIn("입력이 비어 있습니다", out)
        self.assertEqual(out.count("1~5 사이의 숫자"), 2)

    def test_input_text_rejects_empty(self):
        game = self.make_game()
        with patch("builtins.input", side_effect=["", "   ", "내용"]), \
                patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(game.input_text("> "), "내용")


class TestGameFeatures(GameTestBase):
    """퀴즈 풀기 / 추가 / 목록 / 점수 기능 테스트"""

    def test_first_run_uses_default_quizzes(self):
        game = self.make_game()
        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertIsNone(game.best_score)

    def test_play_quiz_all_correct_updates_best_score(self):
        game = self.make_game()
        answers = [str(q.answer) for q in game.quizzes]
        out = run_with_inputs(game.play_quiz, answers)
        self.assertEqual(game.best_score, len(game.quizzes))
        self.assertIn("최고 점수 갱신", out)

    def test_lower_score_does_not_replace_best(self):
        game = self.make_game()
        game.best_score = 5
        wrong = [str(q.answer % 4 + 1) for q in game.quizzes]  # 전부 오답
        run_with_inputs(game.play_quiz, wrong)
        self.assertEqual(game.best_score, 5)

    def test_play_quiz_with_no_quizzes(self):
        game = self.make_game()
        game.quizzes = []
        out = run_with_inputs(game.play_quiz, [])
        self.assertIn("등록된 퀴즈가 없습니다", out)

    def test_add_quiz(self):
        game = self.make_game()
        before = len(game.quizzes)
        run_with_inputs(game.add_quiz, ["새 문제", "a", "b", "c", "d", "3"])
        self.assertEqual(len(game.quizzes), before + 1)
        self.assertEqual(game.quizzes[-1].answer, 3)

    def test_show_list_and_empty_list(self):
        game = self.make_game()
        out = run_with_inputs(game.show_quiz_list, [])
        self.assertIn(f"총 {len(game.quizzes)}개", out)
        game.quizzes = []
        out = run_with_inputs(game.show_quiz_list, [])
        self.assertIn("등록된 퀴즈가 없습니다", out)

    def test_show_score_before_playing(self):
        game = self.make_game()
        out = run_with_inputs(game.show_score, [])
        self.assertIn("아직 퀴즈를 푼 기록이 없습니다", out)


class TestFileIO(GameTestBase):
    """state.json 저장/불러오기 테스트"""

    def test_data_persists_after_restart(self):
        game = self.make_game()
        run_with_inputs(game.add_quiz, ["유지 확인 문제", "a", "b", "c", "d", "1"])
        game.best_score = 4
        game.save()

        reloaded = self.make_game()   # 프로그램을 다시 켠 것과 같음
        self.assertEqual(reloaded.quizzes[-1].question, "유지 확인 문제")
        self.assertEqual(reloaded.best_score, 4)

    def test_saved_file_is_utf8_json(self):
        game = self.make_game()
        game.save()
        with open(self.state_path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("quizzes", data)
        self.assertIn("best_score", data)

    def test_broken_file_restores_defaults(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            f.write("{ 망가진 파일")
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            game = QuizGame()
        self.assertIn("손상", out.getvalue())
        self.assertGreaterEqual(len(game.quizzes), 5)


class TestBackup(GameTestBase):
    """state.json.bak 백업 생성과 백업 기반 복구 테스트"""

    def test_save_creates_backup_of_previous_state(self):
        game = self.make_game()
        game.best_score = 3
        game.save()                      # 첫 저장: 이전 파일이 없으므로 백업 없음
        self.assertFalse(os.path.exists(self.backup_path))
        game.best_score = 5
        game.save()                      # 두 번째 저장: 직전 상태(3점)가 백업됨
        with open(self.backup_path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["best_score"], 3)

    def test_broken_file_restored_from_backup(self):
        game = self.make_game()
        run_with_inputs(game.add_quiz, ["백업 문제", "a", "b", "c", "d", "2"])
        game.best_score = 4
        game.save()                      # 이 시점의 상태가 다음 저장 때 백업됨
        game.save()
        with open(self.state_path, "w", encoding="utf-8") as f:
            f.write("{ 망가진 파일")
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            restored = QuizGame()
        self.assertIn("백업 파일에서 복구", out.getvalue())
        self.assertEqual(restored.quizzes[-1].question, "백업 문제")
        self.assertEqual(restored.best_score, 4)

    def test_broken_file_and_broken_backup_use_defaults(self):
        for path in (self.state_path, self.backup_path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("{ 망가진 파일")
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            game = QuizGame()
        self.assertIn("기본 퀴즈 데이터로 복구", out.getvalue())
        self.assertEqual(len(game.quizzes), 7)
        with open(self.backup_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "{ 망가진 파일")   # 복구 저장이 백업을 덮어쓰지 않음


class TestSafeExit(GameTestBase):
    """Ctrl+C / 입력 종료 시 비정상 종료하지 않고 저장하는지 테스트"""

    def test_keyboard_interrupt_saves_and_exits(self):
        game = self.make_game()
        out = run_with_inputs(game.run, KeyboardInterrupt())
        self.assertIn("안전하게 종료", out)
        self.assertTrue(os.path.exists(self.state_path))

    def test_eof_saves_and_exits(self):
        game = self.make_game()
        out = run_with_inputs(game.run, EOFError())
        self.assertIn("안전하게 종료", out)

    def test_menu_exit(self):
        game = self.make_game()
        out = run_with_inputs(game.run, ["5"])
        self.assertIn("게임을 종료합니다", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
