from django.db import models

class User(models.Model):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
