from unittest import TestCase

from opwen_cloudserver.email.fake import FakeEmailSender
from opwen_cloudserver.lifecycle import ReadDataFromClients
from opwen_cloudserver.remotestorage.fake import FakeRemoteStorage
from opwen_cloudserver.state.fake import InMemoryDeliveredEmailsStore
from opwen_cloudserver.state.fake import InMemoryAccountsStore


class TestLifecycle(TestCase):
    def test(self):
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

        action = ReadDataFromClients(exchange_client, email_client,
                                     account_store, delivered_store)

        action()

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
