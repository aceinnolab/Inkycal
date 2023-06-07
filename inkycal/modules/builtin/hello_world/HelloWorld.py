import inspect
import re


def get_param_docstring(cls, param_name):
    """Provides the docs for a parameter in the init function of a class"""
    init_docstring = inspect.getdoc(cls.__init__)
    pattern = rf"{param_name}:\s+(\s+.*?(?=\n\s*\w+:|$))"
    match = re.search(pattern, init_docstring, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        pretty = re.sub(r"\s+", " ", extracted_text)  # Remove extra spaces and newlines
        pretty = re.sub(r"\s*\n\s*", " ", pretty)
        return pretty
    return None


class HelloWorld:

    def __init__(self, param1: str, param2: int) -> None:
        """Init the HelloWorld module.

        Args:
            param1:
                some string. Some long description of what this param does, although it doesn't
                serve any specific purpose.
            param2:
                some number.

        """
        self.param1 = param1
        self.param2 = param2
        print(f"Init complete with param1 {self.param1} and param2 as {self.param2}")


if __name__ == '__main__':
    keys = HelloWorld.__init__.__code__.co_varnames[1:]
    key_docs = {
        key: get_param_docstring(HelloWorld, key)
        for key in keys
    }
    b = 1
