from re import sub


def clean_cpf(cpf: str) -> str:
    return sub(r'\D', '', cpf)


def validate_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    return True
