import requests

def get_capital_from_context(context):
    response = requests.get('https://en.wikipedia.org/wiki/Capital')
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve capital information from Wikipedia. Status code: {response.status_code}")
    return context.split('. ').pop().strip()