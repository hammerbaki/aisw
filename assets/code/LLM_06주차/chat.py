"""이력을 기억하는 미니 챗봇 (week06 실습 2용).

실행: .venv/bin/python chat.py
종료: 빈 줄 입력

완성할 곳은 TODO 두 곳이다. 답마다 input_tokens를 함께 찍는다(이력이 쌓이면 늘어난다).
"""

import os

import anthropic

MODEL = os.environ.get("COURSE_MODEL", "claude-haiku-4-5-20251001")
SYSTEM = "너는 친절한 도우미다. 두세 문장 이내로 간단히 답한다."
STREAM = False                      # True로 바꾸면 답이 흘러나온다

client = anthropic.Anthropic()
history = []                        # 지금까지의 대화가 쌓이는 곳


def ask(question: str) -> str:
    """질문을 보내고 답을 돌려준다."""

    # TODO 1: 이번 질문을 history에 넣는다.
    #         history.append({"role": "user", "content": question})

    # history가 비어 있으면 이번 질문만 보낸다 (TODO 1을 완성하기 전의 임시 동작)
    messages = history or [{"role": "user", "content": question}]

    if STREAM:
        answer = ""
        print("AI: ", end="", flush=True)
        with client.messages.stream(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM,
            messages=messages,
        ) as stream:
            for piece in stream.text_stream:
                print(piece, end="", flush=True)
                answer += piece
            usage = stream.get_final_message().usage
        print(f"\n   (input_tokens={usage.input_tokens}, output_tokens={usage.output_tokens})")
    else:
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM,
            messages=messages,
        )
        answer = response.content[0].text
        print(f"AI: {answer}")
        print(f"   (input_tokens={response.usage.input_tokens}, output_tokens={response.usage.output_tokens})")

    # TODO 2: 이번 답을 history에 넣는다.
    #         history.append({"role": "assistant", "content": answer})

    return answer


if __name__ == "__main__":
    print("미니 챗봇입니다. 빈 줄을 입력하면 끝납니다.")
    while True:
        try:
            question = input("\n나: ").strip()
        except EOFError:          # Ctrl+D
            question = ""
        if not question:
            print("종료합니다.")
            break
        ask(question)
