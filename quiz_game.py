"""게임 전체(메뉴, 진행, 점수)를 관리하는 QuizGame 클래스"""
from quiz import Quiz
from default_data import get_default_quizzes

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
        self.quizzes = get_default_quizzes()   # Quiz 객체 목록
        self.best_score = None                 # 최고 점수 (아직 안 풀었으면 None)

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

    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
        print("\n[퀴즈 추가]")
        question = self.input_text("문제: ")
        choices = [self.input_text(f"선택지 {i}: ") for i in range(1, 5)]
        answer = self.input_number("정답 번호(1~4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
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
                print("게임을 종료합니다. 안녕히 가세요!")
                break
