import abc
import sys

try:
    input = raw_input
except NameError:
    pass


class Tag(object):
    prompt_text = "Propose a value for the '{key}' tag: "

    def __init__(self, key):
        self.key = key
        self.value = None
        self.prompt = None

    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def withValue(self, value):
        pass

    def get_user_proposal(self, justify_width=0):
        self._print_prompt(justify_width)
        self.value = input()

        if not self.validate():
            print("Tag must not be empty")
            return self.get_user_proposal(justify_width)
        return self

    def _print_prompt(self, justify_width=0):
        sys.stdout.write(self._prompt_text().ljust(justify_width))
        sys.stdout.flush()

    def _prompt_text(self):
        return self.prompt_text.format(self.key)

    def __eq__(self, other):
        if type(self) == type(other):
            return (other.value == self.value) \
                   and (other.key == self.key)
        if isinstance(other, basestring):
            return other == self.key and \
                   self.value is None
        return False

    @property
    def prompt_width(self):
        return len(self.prompt_text.format(key=self.key))


class TagString(Tag):
    def validate(self):
        return isinstance(self.value, basestring)

    def withValue(self, value):
        tag = TagString(self.key)
        tag.value = value
        return tag


class TagCategorical(Tag):
    prompt_text = "Select a value for the '{key}' tag:"

    def __init__(self, key, categories):
        super(TagCategorical, self).__init__(key)
        self.categories = categories

    def __eq__(self, other):
        if super(TagCategorical, self).__eq__(other):
            return self.categories == other.categories
        return False

    def _prompt_text(self):
        text = self.prompt_text.format(key=self.key) + "\n"
        for i, option in enumerate(self.categories):
            text += " [{i}] {option}\n".format(
                i=i, option=option
            )
        return text + "> "

    def get_user_proposal(self, justify_width=0):
        super(TagCategorical, self).get_user_proposal(justify_width)
        self.value = self.categories[int(self.value)]
        return self

    def validate(self):
        return self.value.isdigit() \
               and (0 <= int(self.value) < len(self.categories))

    def withValue(self, value):
        tag = TagCategorical(self.key, self.categories)
        tag.value = value
        return tag
