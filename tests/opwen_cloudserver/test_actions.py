from unittest import TestCase
from unittest import skipUnless

from opwen_cloudserver.services.remotestorage.azure import AzureRemoteStorage

from config import Config
from opwen_cloudserver.actions import ReadDataFromClients
from opwen_cloudserver.services.email.sendgrid import SendGridEmailSender
from opwen_cloudserver.state.sql import SqlAccountsStore
from opwen_cloudserver.state.sql import SqlDeliveredEmailsStore
from tests.utils.fakes import FakeEmailSender
from tests.utils.fakes import FakeRemoteStorage
from tests.utils.fakes import InMemoryAccountsStore
from tests.utils.fakes import InMemoryDeliveredEmailsStore


class TestReadDataFromClients(TestCase):
    @skipUnless(Config.RUN_INTEGRATION_TESTS, 'integration tests disabled')
    def test_end_to_end(self):
        read_data_from_clients = ReadDataFromClients(
            exchange_client=AzureRemoteStorage(
                account_key=Config.STORAGE_ACCOUNT_KEY,
                account_name=Config.STORAGE_ACCOUNT_NAME,
                container=Config.STORAGE_ACCOUNT_CONTAINER),
            email_client=SendGridEmailSender(
                apikey=Config.EMAIL_ACCOUNT_KEY),
            account_store=SqlAccountsStore(
                database_uri=Config.SQLALCHEMY_DATABASE_URI,
                email_host=Config.EMAIL_HOST),
            delivered_store=SqlDeliveredEmailsStore(
                database_uri=Config.SQLALCHEMY_DATABASE_URI))

        read_data_from_clients()

    def test_fakes(self):
        test_client, test_host = 'client1', 'thehost.ca'
        new_user, existing_user = 'koala', 'bear'

        account_store = InMemoryAccountsStore(email_host=test_host)
        existing_email = account_store.create(test_client, existing_user)

        email_from_new_user = {
            'from': new_user,
            'to': ['test@test.net'],
            'subject': 'hi from new user',
        }
        email_from_existing_user = {
            'from': existing_email,
            'to': ['test@somehost.org'],
            'subject': 'hi again',
        }
        already_delivered_email = {
            'from': existing_email,
            'to': ['old@delivered.org'],
            'subject': 'hi in the past',
        }

        exchange_client = FakeRemoteStorage({
            test_client: {
                'emails': [
                    email_from_existing_user,
                    email_from_new_user,
                    already_delivered_email,
                ],
                'accounts': [
                    {'name': new_user},
                ],
            },
        })

        delivered_store = InMemoryDeliveredEmailsStore()
        delivered_store.add(test_client, already_delivered_email)

        email_client = FakeEmailSender()

        read_data_from_clients = ReadDataFromClients(
            exchange_client=exchange_client,
            email_client=email_client,
            account_store=account_store,
            delivered_store=delivered_store)

        read_data_from_clients()

        self.assertNotIn(already_delivered_email, email_client.sent)
        self.assertEqual(2, len(email_client.sent))
        self.assertEqual(email_from_existing_user, email_client.sent[0])
        self.assertEqual(email_from_new_user['subject'],
                         email_client.sent[1]['subject'])
        self.assertEqual(email_from_new_user['to'],
                         email_client.sent[1]['to'])
        self.assertIn('@', email_client.sent[1]['from'])
        self.assertIn(test_host, email_client.sent[1]['from'])
        self.assertIn(test_client, email_client.sent[1]['from'])
