def stripped_text(text: str, max_length: int) -> str:
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


if __name__ == '__main__':
    print(stripped_text("""A function or method that is called when the button is pressed""", 15))
