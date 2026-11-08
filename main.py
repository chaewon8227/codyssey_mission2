"""야구 규칙 퀴즈 게임 - 실행 파일"""
from default_data import get_default_quizzes
from quiz import Quiz

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


def input_number(prompt, min_value, max_value):
    """min_value~max_value 사이의 숫자를 받을 때까지 다시 묻는다."""
    while True:
        text = input(prompt).strip()          # 앞뒤 공백 제거
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


def play_quiz(quizzes):
    """저장된 퀴즈를 순서대로 출제하고 맞힌 개수를 돌려준다."""
    if not quizzes:
        print("⚠ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
        return None
    correct = 0
    for i, quiz in enumerate(quizzes, start=1):
        quiz.display(i)
        user_answer = input_number("정답 번호: ", 1, 4)
        if quiz.is_correct(user_answer):
            print("⭕ 정답입니다!")
            correct += 1
        else:
            print(f"❌ 오답입니다. 정답은 {quiz.answer}번입니다.")
    print(f"\n결과: {len(quizzes)}문제 중 {correct}문제 정답!")
    return correct


def input_text(prompt):
    """빈 값이 아닌 문자열을 받을 때까지 다시 묻는다."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("⚠ 내용을 입력해 주세요.")


def add_quiz(quizzes):
    """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
    print("\n[퀴즈 추가]")
    question = input_text("문제: ")
    choices = []
    for i in range(1, 5):
        choices.append(input_text(f"선택지 {i}: "))
    answer = input_number("정답 번호(1~4): ", 1, 4)
    quizzes.append(Quiz(question, choices, answer))
    print("✅ 퀴즈가 추가되었습니다.")


def main():
    quizzes = get_default_quizzes()
    while True:
        print(MENU_TEXT)
        choice = input_number("선택: ", 1, 5)
        if choice == 1:
            play_quiz(quizzes)
        elif choice == 2:
            add_quiz(quizzes)
        elif choice == 3:
            print("[퀴즈 목록] 준비 중입니다.")
        elif choice == 4:
            print("[점수 확인] 준비 중입니다.")
        else:
            print("게임을 종료합니다. 안녕히 가세요!")
            break


if __name__ == "__main__":
    main()
