from django.test import TestCase

from books.blockchain import Blockchain

# Create your tests here.
class BlockchainTestCase(TestCase):

    def test_comms(self):
        resp = Blockchain.getinfo()
        self.assertEqual(resp['errors'], '')