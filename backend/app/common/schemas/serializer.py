from datetime import datetime


def to_camel(string: str) -> str:
    """used in the custom base model as the "alias generator"
    meaning, the model will accept a camel case field name and
    also the python snake case field name
    Arguments:
        string {str} -- the string to convert to camel case
    Returns:
        str -- the string in camel case
    """
    words = string.split("_")
    new_name = []
    for i, word in enumerate(words):
        if i:
            new_name.append(word.capitalize())
        else:
            new_name.append(word.lower())

    return "".join(new_name).replace("Id", "ID")


def datetime_string(dt: datetime) -> str:
    """the standardized format the API returns dates in"""
    return dt.strftime("%Y-%m-%d %H:%M")
