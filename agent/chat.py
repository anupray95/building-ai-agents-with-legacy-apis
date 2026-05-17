def chatCompletion(client, conversation_history, model):
    response = client.chat.completions.create(
        model=model,
        messages=conversation_history,
        max_tokens=1000,
    )
    return response.choices[0].message.content.strip()
