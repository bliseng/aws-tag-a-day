from prompt_toolkit.validation import Validator, ValidationError


class NumberRangeValidator(Validator):
    def __init__(self, range=None):
        self._range = range

    def validate(self, document):
        text = document.text

        if text and not text.isdigit():
            for i, c in enumerate(text):
                if not c.isdigit():
                    break
            raise ValidationError(
                message='Please enter a number', cursor_position=i)
