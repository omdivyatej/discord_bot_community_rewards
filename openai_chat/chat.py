import openai


def get_answers_from_knowledge_base(question):
    client = openai.OpenAI(base_url="https://0x2e41e521280453caeb6c5d10971fc05a8d14aa52.us.gaianet.network/v1", api_key="sk-proj-243cBhAlJDYP4Vz60kKuT3BlbkFJdAJTxivmJ23BklvSviQy")

    response = client.chat.completions.create(
        model="Meta-Llama-3-8B-Instruct-Q5_K_M",
        messages=[
            {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=500,
    )
    return response.choices[0].message.content