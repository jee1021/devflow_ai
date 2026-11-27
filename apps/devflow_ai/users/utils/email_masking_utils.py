

def mask_email(email: str)-> str:

    try:
        local, domain, sep = email.split('@')
        local, domain = local.split('.'), domain.split('.')
    except ValueError:
        raise ValueError(
            "유효하지 않은 이메일 주소입니다: {}".format(email)
        )
    return f"{local}@{domain}.{sep}"


