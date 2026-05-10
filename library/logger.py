
def str_head(string: str) -> str:
    pos = string.find('\n')

    if pos >= 1024:
        return string[:1024] + '\n'

    return string[:pos] + '\n'


def log_exception(e: Exception):
    print('Handled Exception:', str_head(str(e)), flush=True)

    with open('exceptions.log', 'a') as f:
        f.write(str(e))
