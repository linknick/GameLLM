"""Example tool that counts letters in a string.
In real app, your tools will be more complex and have JSON schema validation.
"""


def count_letters(input_string: str, target_character: str) -> int:
    print(f"{input_string},{target_character}")
    return input_string.count(target_character)

if __name__ == "__main__":
    a = input()
    b = input()
    print(count_letters(a,b))