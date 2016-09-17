from opwen_cloudserver.email import EmailSender


class FakeEmailSender(EmailSender):
    def __init__(self):
        self.sent = []

    def send_email(self, email):
        self.sent.append(email)
        return True
