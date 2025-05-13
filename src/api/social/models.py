from django.db import models
from api.user.models import User

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_relations', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='follower_relations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.name} follows {self.following.name}"

    class Meta:
        db_table = 'follows'
        ordering = ['-created_at']