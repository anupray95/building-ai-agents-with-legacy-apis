def chatCompletion(client, system_prompt='', conversation_history=[], user_message=''):
    messages = (
        [{"role": "system", "content": system_prompt}]
        + conversation_history
        + [{"role": "user", "content": user_message}]
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        max_tokens=100,
    )

    return response.choices[0].message.content.strip()
