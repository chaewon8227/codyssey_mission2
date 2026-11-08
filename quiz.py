"""개별 퀴즈 한 문제를 표현하는 Quiz 클래스"""


class Quiz:
    def __init__(self, question, choices, answer):
        self.question = question    # 문제 (str)
        self.choices = choices      # 선택지 4개 (list of str)
        self.answer = answer        # 정답 번호 1~4 (int)

    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        title = f"Q{number}. " if number is not None else ""
        print(f"\n{title}{self.question}")
        for i, choice in enumerate(self.choices, start=1):
            print(f"  {i}) {choice}")

    def is_correct(self, user_answer):
        """사용자가 고른 번호가 정답이면 True."""
        return user_answer == self.answer

    def to_dict(self):
        """JSON 저장용 딕셔너리로 변환한다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Quiz 객체를 만든다. 형식이 틀리면 ValueError."""
        question = data["question"]
        choices = data["choices"]
        answer = data["answer"]
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제가 비어 있습니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")
        if not isinstance(answer, int) or not 1 <= answer <= 4:
            raise ValueError("정답은 1~4 사이여야 합니다.")
        return cls(question, [str(c) for c in choices], answer)
