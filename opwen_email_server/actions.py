class ReceiveEmail(object):
    def __init__(self, email_store, email_receiver):
        """
        :type email_store: opwen_domain.email.EmailStore
        :type email_receiver: opwen_domain.mailbox.EmailReceiver

        """
        self._email_store = email_store
        self._email_receiver = email_receiver

    def __call__(self, request):
        """
        :type request: flask.Request

        """
        received_email = self._email_receiver.parse_email(request)
        self._email_store.create([received_email])


class UploadEmailsToClients(object):
    def __init__(self, email_store, email_sync):
        """
        :type email_store: opwen_domain.email.EmailStore
        :type email_sync: opwen_domain.sync.Sync

        """
        self._email_store = email_store
        self._email_sync = email_sync

    def __call__(self):
        emails = list(self._email_store.pending())
        self._email_sync.upload(emails)
        self._email_store.mark_sent(emails)


class DownloadEmailsFromClients(object):
    def __init__(self, email_store, email_sync):
        """
        :type email_store: opwen_domain.email.EmailStore
        :type email_sync: opwen_domain.sync.Sync

        """
        self._email_store = email_store
        self._email_sync = email_sync

    def __call__(self):
        emails = self._email_sync.download()
        self._email_store.create(emails)


class SendEmailsFromClients(object):
    def __init__(self, email_store, email_sender):
        """
        :type email_store: opwen_domain.email.EmailStore
        :type email_sender: opwen_domain.mailbox.EmailSender

        """
        self._email_store = email_store
        self._email_sender = email_sender

    def __call__(self):
        sent = []
        for email in self._email_store.pending():
            if self._email_sender.send_email(email):
                sent.append(email)
        self._email_store.mark_sent(sent)
