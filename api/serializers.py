from rest_framework import serializers
from .models import Profile, Post, Category, Tag, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True}}


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "groups", "profile_pic", "gender"]

    def get_profile_pic(self, obj):
        try:
            profile = Profile.objects.get(user_id=obj.id)
            return "http://127.0.0.1:8000" + profile.profile_pic.url
        except Profile.DoesNotExist:
            return "http://127.0.0.1:8000/media/user_profile/blank-picture.png"
    def get_gender(sefl, obj):
        try:
            profile = Profile.objects.get(user_id=obj.id)
            return profile.gender
        except Profile.DoesNotExist:
            return ""

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # # Add custom claims
        token['user'] = UserSerializer(user).data
        # ...
        return token

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "main_category", "sub_category"]

class PostSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = CategorySerializer()
    tags = serializers.SerializerMethodField()
    author = UserSerializer(source="user")
    comment_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ["id", "author", "thumbnail", "title", "sapo", "body", "created_at", "updated_at", "category", "tags", "view_count", "comment_count"]
    def get_thumbnail(self, obj):
        return "http://127.0.0.1:8000"+obj.thumbnail.url
    def get_tags(self, obj):
        tags = obj.tags.all()
        return [tag.tag_name for tag in tags]
    def get_comment_count(self, obj):
        return Comment.objects.filter(post_id=obj.id).count()
    
class PostSummarySerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "thumbnail", "title", "sapo", "created_at"]
    def get_thumbnail(self, obj):
        return "http://127.0.0.1:8000"+obj.thumbnail.url

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "tag_name", "tag_count", "created_at"]
    

class CommentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()
    parent_id = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ["id", "name", "avatar", "content", "created_at", 'is_like', 'parent_id', 'like']

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
    def get_avatar(self, obj):
        try:
            profile = Profile.objects.get(user_id=obj.user.id)
            return "http://127.0.0.1:8000" + profile.profile_pic.url
        except Profile.DoesNotExist:
            return "http://127.0.0.1:8000/media/user_profile/blank-picture.png"
    def get_is_like(self, obj):
        if self.context['user'] in obj.user_like.all():
            return True
        else:   
            return False
    def get_like(self, obj):
        return obj.user_like.all().count()
    def get_parent_id(self, obj):
        if obj.parent:
            return obj.parent.id
        else:
            return None