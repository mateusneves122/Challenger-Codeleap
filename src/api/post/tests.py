from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from api.user.models import User
from .models import Post
from django.utils import timezone


class PostAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(name='Test User 1', email='test1@example.com', password_hash='hashedpassword1')
        self.user2 = User.objects.create(name='Test User 2', email='test2@example.com', password_hash='hashedpassword2')

        self.post1_user1 = Post.objects.create(user=self.user1, title='Post 1 by User 1', content='Content 1')
        self.post2_user1 = Post.objects.create(user=self.user1, title='Post 2 by User 1', content='Content 2')
        self.post1_user2 = Post.objects.create(user=self.user2, title='Post 1 by User 2', content='Content 3')

        self.create_post_url = reverse('create_post')
        self.list_user_posts_url_user1 = reverse('list_user_posts', kwargs={'user_id': self.user1.id})
        self.list_user_posts_url_user2 = reverse('list_user_posts', kwargs={'user_id': self.user2.id})
        self.post_detail_url_post1_user1 = reverse('post_detail_operations', kwargs={'post_id': self.post1_user1.id})

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'New Post', 'content': 'New Content'}
        response = self.client.post(self.create_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 4) # 3 from setUp + 1 new
        self.assertEqual(response.data['title'], 'New Post')
        self.assertEqual(response.data['user'], self.user1.id)

    def test_create_post_unauthenticated(self):
        data = {'title': 'New Post', 'content': 'New Content'}
        response = self.client.post(self.create_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_invalid_data(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': '', 'content': 'New Content'} # Invalid: title is required
        response = self.client.post(self.create_post_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_list_user_posts_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_user_posts_url_user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # User1 has 2 posts
        self.assertEqual(response.data[0]['title'], self.post2_user1.title) # Ordered by -created_at
        self.assertEqual(response.data[1]['title'], self.post1_user1.title)

    def test_list_user_posts_unauthenticated(self):
        response = self.client.get(self.list_user_posts_url_user1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_posts_user_not_found(self):
        self.client.force_authenticate(user=self.user1)
        non_existent_user_id = 999
        url = reverse('list_user_posts', kwargs={'user_id': non_existent_user_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "User not found.")

    def test_get_post_detail_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.post_detail_url_post1_user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post1_user1.title)
        self.assertEqual(response.data['id'], self.post1_user1.id)

    def test_get_post_detail_unauthenticated(self):
        response = self.client.get(self.post_detail_url_post1_user1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_post_detail_not_found(self):
        self.client.force_authenticate(user=self.user1)
        non_existent_post_id = 999
        url = reverse('post_detail_operations', kwargs={'post_id': non_existent_post_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Post not found or has been deleted.")

    def test_get_post_detail_deleted_post(self):
        self.client.force_authenticate(user=self.user1)
        self.post1_user1.deleted_at = timezone.now()
        self.post1_user1.save()
        response = self.client.get(self.post_detail_url_post1_user1)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_post_authenticated_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.patch(self.post_detail_url_post1_user1, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1_user1.refresh_from_db()
        self.assertEqual(self.post1_user1.title, 'Updated Title')
        self.assertEqual(self.post1_user1.content, 'Updated Content')

    def test_update_post_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.user2) # User2 trying to update User1's post
        data = {'title': 'Updated Title by User 2'}
        response = self.client.patch(self.post_detail_url_post1_user1, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to edit this post.")

    def test_update_post_unauthenticated(self):
        data = {'title': 'Updated Title'}
        response = self.client.patch(self.post_detail_url_post1_user1, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_not_found(self):
        self.client.force_authenticate(user=self.user1)
        non_existent_post_id = 999
        url = reverse('post_detail_operations', kwargs={'post_id': non_existent_post_id})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_post_partial(self):
        self.client.force_authenticate(user=self.user1)
        data = {'title': 'Partially Updated Title'}
        original_content = self.post1_user1.content
        response = self.client.patch(self.post_detail_url_post1_user1, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post1_user1.refresh_from_db()
        self.assertEqual(self.post1_user1.title, 'Partially Updated Title')
        self.assertEqual(self.post1_user1.content, original_content) # Content should remain unchanged

    def test_delete_post_authenticated_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.post_detail_url_post1_user1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.post1_user1.refresh_from_db()
        self.assertIsNotNone(self.post1_user1.deleted_at)

        get_response = self.client.get(self.post_detail_url_post1_user1)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

        list_response = self.client.get(self.list_user_posts_url_user1)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

    def test_delete_post_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.post_detail_url_post1_user1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to delete this post.")
        self.post1_user1.refresh_from_db()
        self.assertIsNone(self.post1_user1.deleted_at)

    def test_delete_post_unauthenticated(self):
        response = self.client.delete(self.post_detail_url_post1_user1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_post_not_found(self):
        self.client.force_authenticate(user=self.user1)
        non_existent_post_id = 999
        url = reverse('post_detail_operations', kwargs={'post_id': non_existent_post_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_already_deleted_post(self):
        self.client.force_authenticate(user=self.user1)
        response_first_delete = self.client.delete(self.post_detail_url_post1_user1)
        self.assertEqual(response_first_delete.status_code, status.HTTP_204_NO_CONTENT)
        
        response_get_deleted = self.client.get(self.post_detail_url_post1_user1)
        self.assertEqual(response_get_deleted.status_code, status.HTTP_404_NOT_FOUND)

        response_second_delete = self.client.delete(self.post_detail_url_post1_user1)
        self.assertEqual(response_second_delete.status_code, status.HTTP_404_NOT_FOUND)
