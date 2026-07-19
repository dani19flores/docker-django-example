from django.core.exceptions import ValidationError

BLOCKED_WORDS = [
    'barato', 
    'malo'
]

def validate_blocked_words(value):
    init_string = f"{value}".lower()
    unique_words = set(init_string.split())
    blocked_words = set(BLOCKED_WORDS)
    invalid_words = (unique_words & blocked_words)
    has_error = len(invalid_words) > 0
    if has_error:
        erros = []
        for invalid_word in enumerate(invalid_words):
            msg = "{} es una palabra no permitida".format(invalid_word)
            erros.append(msg)
        raise ValidationError(erros)
    return value