from ninja.responses import Response


class PhoneSendOut(Response):
    message: str
    expires_in: int
    debug_code: str | None = None

class EmailSendOut(Response):
    message: str
    expires_in: int
    debug_code: str | None = None