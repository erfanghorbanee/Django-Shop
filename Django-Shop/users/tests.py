# from threading import Thread

# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase
# from django.urls import reverse

# from .models import Address


# class PrimaryAddressRaceTest(TestCase):
#     def setUp(self):
#         self.user = get_user_model().objects.create_user(
#             email="race@example.com",
#             password="testpass",
#             first_name="A",
#             last_name="B",
#             phone="+1234567890",
#         )
#         self.addr1 = Address.objects.create(
#             user=self.user,
#             street_address="1 Main St",
#             city="City",
#             state="State",
#             zip_code="12345",
#             country="Country",
#             is_primary=False,
#         )
#         self.addr2 = Address.objects.create(
#             user=self.user,
#             street_address="2 Main St",
#             city="City",
#             state="State",
#             zip_code="12345",
#             country="Country",
#             is_primary=False,
#         )
#         self.client1 = Client()
#         self.client2 = Client()
#         self.client1.login(email="race@example.com", password="testpass")
#         self.client2.login(email="race@example.com", password="testpass")

#     def promote(self, client, address_id, results, idx):
#         url = reverse("users:set_primary_address", args=[address_id])
#         response = client.post(url)
#         results[idx] = response

#     def test_concurrent_primary_promotions(self):
#         # Simulate two concurrent requests
#         results = [None, None]
#         t1 = Thread(target=self.promote, args=(self.client1, self.addr1.id, results, 0))
#         t2 = Thread(target=self.promote, args=(self.client2, self.addr2.id, results, 1))
#         t1.start()
#         t2.start()
#         t1.join()
#         t2.join()

#         # Refresh addresses
#         addr1 = Address.objects.get(id=self.addr1.id)
#         addr2 = Address.objects.get(id=self.addr2.id)
#         primaries = [a for a in [addr1, addr2] if a.is_primary]
#         self.assertEqual(
#             len(primaries), 1, "Only one address should be primary after race."
#         )

#         # Check that at least one response contains the error message
#         found_error = any(
#             b"Could not set address as primary due to a conflict" in r.content
#             for r in results
#             if r is not None
#         )
#         self.assertTrue(
#             found_error, "Error message should be shown for race condition."
#         )
