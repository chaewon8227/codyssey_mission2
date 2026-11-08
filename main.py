"""야구 규칙 퀴즈 게임 - 실행 파일"""

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


def main():
    while True:
        print(MENU_TEXT)
        choice = input_number("선택: ", 1, 5)
        if choice == 1:
            print("[퀴즈 풀기] 준비 중입니다.")
        elif choice == 2:
            print("[퀴즈 추가] 준비 중입니다.")
        elif choice == 3:
            print("[퀴즈 목록] 준비 중입니다.")
        elif choice == 4:
            print("[점수 확인] 준비 중입니다.")
        else:
            print("게임을 종료합니다. 안녕히 가세요!")
            break


if __name__ == "__main__":
    main()
