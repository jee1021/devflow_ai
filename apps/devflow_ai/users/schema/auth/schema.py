from ninja import Schema


class PhoneSendIn(Schema):
    phone: str
    captcha_token: str = ""


class VerifyIn(Schema):
    phone: str
    code: str
