class ReadDataFromClients(object):
    def __init__(self, exchange_client, email_client,
                 account_store, delivered_store):
        """
        :type exchange_client: opwen_cloudserver.remotestorage.RemoteStorage
        :type email_client: opwen_cloudserver.email.EmailSender
        :type account_store: opwen_cloudserver.state.AccountsStore
        :type delivered_store: opwen_cloudserver.state.DeliveredEmailsStore

        """
        self._exchange_client = exchange_client
        self._email_client = email_client
        self._account_store = account_store
        self._delivered_store = delivered_store

    def __call__(self):
        for client_name in self._list_clients():
            self._handle_upload_for_client(client_name)

    def _list_clients(self):
        """
        :rtype: collections.Iterable[str]

        """
        return self._exchange_client.list_roots()

    def _handle_upload_for_client(self, client_name):
        """
        :type client_name: str

        """
        upload = self._exchange_client.download(client_name)

        for new_account in upload.accounts:
            self._create_email_account(client_name, new_account)

        success = all(self._send_email(client_name, new_email)
                      for new_email in upload.emails)

        if success:
            self._delete_state(client_name)

    def _create_email_account(self, client_name, account):
        """
        :type client_name: str
        :type account: dict

        """
        self._account_store.create(client_name, account.get('name'))

    def _send_email(self, client_name, email):
        """
        :type client_name: str
        :type email: dict
        :rtype bool

        """
        if self._delivered_store.contains(client_name, email):
            return True

        email['from'] = self._account_store.get(client_name, email.get('from'))
        sent = self._email_client.send_email(email)
        if sent:
            self._delivered_store.add(client_name, email)

        return sent

    def _delete_state(self, client_name):
        """
        :type client_name: str

        """
        self._exchange_client.delete(client_name)
        self._delivered_store.delete(client_name)
