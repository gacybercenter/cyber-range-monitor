from datetime import datetime

def to_camel(string: str) -> str:
    '''used in the custom base model as the "alias generator"
    meaning, the model will accept a camel case field name and
    also the python snake case field name
    
    Arguments:
        string {str} -- the string to convert to camel case

    Returns:
        str -- the string in camel case
    '''
    return ''.join(
        word.capitalize() if i else word
        for i, word in enumerate(string.split('_'))
    )


def dt_serializer(dt: datetime) -> str:
    """the standardized format the API returns dates in"""
    return dt.strftime("%Y-%m-%d %H:%M")


