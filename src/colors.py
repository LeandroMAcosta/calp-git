colors = {
    "CYAN" : '\033[96m',
    "GREEN" : '\033[92m',
    "YELLOW" : '\033[93m',
    "RED" : '\033[91m',
}


def color_text(color, message):
    return f"{colors[color]}{message}\033[00m"