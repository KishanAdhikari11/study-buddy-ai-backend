def generate_flashcards(content):
    prompt = f"""
    Create flashcards from the following content:
    {content}

    Format:
    - Q: What is ...?
      A: ...
    """
    response = llm.complete(prompt)
    return response.text
