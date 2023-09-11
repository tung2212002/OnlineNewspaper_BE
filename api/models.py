from django.db import models
from django.contrib.auth import get_user_model
import uuid
import mptt
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.

User = get_user_model()


# Profile
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to="user_profile",
        default="user_profile/blank-picture.png",
    )
    email = models.EmailField(max_length=50, blank=True)
    gender = models.CharField(max_length=10, blank=True)


class Category(models.Model):
    main_category = models.CharField(max_length=255, blank=True)
    sub_category = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.main_category + " - " + self.sub_category


class Tag(models.Model):
    tag_name = models.CharField(max_length=255, blank=True)
    tag_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag_name


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail = models.ImageField(
        upload_to="thumbnails",
        default="user_post/blank-picture.png",
    )
    title = models.CharField(max_length=500, blank=False)
    sapo = models.TextField(blank=True)
    body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField(Tag)
    view_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.thumbnail:
            self.thumbnail.name = self.thumbnail.name.replace('http://127.0.0.1:8000/media/thumbnails/', '')
        super().save(*args, **kwargs)

class Comment(MPTTModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    content = models.TextField(blank=False)
    user_like = models.ManyToManyField(User, related_name="user_like", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if len(self.content) > 50:
            return self.content[:50] + "..."
        else:
            return self.content
