def chatCompletion(client, system_prompt='', conversation_history=[], user_message='', model='gpt-3.5-turbo-1106'):
    # messages = (
    #     [{"role": "system", "content": system_prompt}]
    #     + conversation_history
    #     + [{"role": "user", "content": user_message}]
    # )

    response = client.chat.completions.create(
        model=model,
        messages=conversation_history,
        max_tokens=1000,
    )

    return response.choices[0].message.content.strip()
