import requests
from colorama import Fore, Style

def execute_http_request(params):
    print(f"{Fore.BLUE}[HTTP]{Style.RESET_ALL} Fetching {params['url']}...")
    response = requests.get(params['url'])
    return response.text

def execute_terminal_log(params, input_data):
    print(f"{Fore.GREEN}[LOG]{Style.RESET_ALL} {params['prefix']} {input_data}")
    return input_data