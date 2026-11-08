"""게임 전체(메뉴, 진행, 점수)를 관리하는 QuizGame 클래스"""
import json
import os

from quiz import Quiz
from default_data import get_default_quizzes

# 프로젝트 루트(이 파일이 있는 폴더)의 state.json
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

MENU_TEXT = """
========================================
        ⚾ 야구 규칙 퀴즈 게임 ⚾
========================================
1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 종료
========================================"""


class QuizGame:
    def __init__(self):
        self.quizzes = []        # Quiz 객체 목록
        self.best_score = None   # 최고 점수 (아직 안 풀었으면 None)
        self.load()

    # ---------- 파일 저장/불러오기 ----------
    def load(self):
        """state.json에서 퀴즈와 최고 점수를 불러온다."""
        if not os.path.exists(STATE_FILE):
            # 첫 실행: 기본 퀴즈 사용
            self.quizzes = get_default_quizzes()
            self.best_score = None
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.quizzes = [Quiz.from_dict(q) for q in data["quizzes"]]
            best = data.get("best_score")
            if best is not None and not isinstance(best, int):
                raise ValueError("best_score 형식 오류")
            self.best_score = best
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError):
            print("⚠ 데이터 파일이 손상되었습니다. 기본 퀴즈 데이터로 복구합니다.")
            self.quizzes = get_default_quizzes()
            self.best_score = None
            self.save()

    def save(self):
        """현재 퀴즈와 최고 점수를 state.json에 저장한다."""
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"⚠ 저장 중 오류가 발생했습니다: {e}")

    # ---------- 입력 처리 ----------
    def input_number(self, prompt, min_value, max_value):
        """min_value~max_value 사이의 숫자를 받을 때까지 다시 묻는다."""
        while True:
            text = input(prompt).strip()
            if text == "":
                print("⚠ 입력이 비어 있습니다. 숫자를 입력해 주세요.")
                continue
            try:
                number = int(text)
            except ValueError:
                print("⚠ 숫자만 입력해 주세요.")
                continue
            if number < min_value or number > max_value:
                print(f"⚠ {min_value}~{max_value} 사이의 숫자를 입력해 주세요.")
                continue
            return number

    def input_text(self, prompt):
        """빈 값이 아닌 문자열을 받을 때까지 다시 묻는다."""
        while True:
            text = input(prompt).strip()
            if text:
                return text
            print("⚠ 내용을 입력해 주세요.")

    # ---------- 메뉴 기능 ----------
    def show_menu(self):
        print(MENU_TEXT)

    def play_quiz(self):
        """퀴즈를 출제하고, 끝나면 최고 점수와 비교해 갱신한다."""
        if not self.quizzes:
            print("⚠ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return
        correct = 0
        for i, quiz in enumerate(self.quizzes, start=1):
            quiz.display(i)
            user_answer = self.input_number("정답 번호: ", 1, 4)
            if quiz.is_correct(user_answer):
                print("⭕ 정답입니다!")
                correct += 1
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.")
        print(f"\n결과: {len(self.quizzes)}문제 중 {correct}문제 정답!")
        if self.best_score is None or correct > self.best_score:
            self.best_score = correct
            print("🏆 최고 점수 갱신!")
            self.save()

    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
        print("\n[퀴즈 추가]")
        question = self.input_text("문제: ")
        choices = [self.input_text(f"선택지 {i}: ") for i in range(1, 5)]
        answer = self.input_number("정답 번호(1~4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        self.save()
        print("✅ 퀴즈가 추가되었습니다.")

    def show_quiz_list(self):
        """등록된 퀴즈의 문제 목록을 보여준다."""
        if not self.quizzes:
            print("⚠ 등록된 퀴즈가 없습니다.")
            return
        print(f"\n[퀴즈 목록] 총 {len(self.quizzes)}개")
        for i, quiz in enumerate(self.quizzes, start=1):
            print(f"  {i}. {quiz.question}")

    def show_score(self):
        """최고 점수를 보여준다."""
        if self.best_score is None:
            print("⚠ 아직 퀴즈를 푼 기록이 없습니다.")
        else:
            print(f"🏆 최고 점수: {self.best_score}문제 정답")

    # ---------- 실행 ----------
    def run(self):
        """메뉴 루프 실행. Ctrl+C나 입력 종료에도 저장 후 안전하게 끝낸다."""
        try:
            self.menu_loop()
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠ 입력이 중단되었습니다. 저장 후 안전하게 종료합니다.")
            self.save()

    def menu_loop(self):
        """메뉴를 반복해서 보여주고 선택한 기능을 실행한다."""
        while True:
            self.show_menu()
            choice = self.input_number("선택: ", 1, 5)
            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_quiz_list()
            elif choice == 4:
                self.show_score()
            else:
                self.save()
                print("게임을 종료합니다. 안녕히 가세요!")
                break
