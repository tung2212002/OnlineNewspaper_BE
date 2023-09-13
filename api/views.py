from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly, IsAdminOrAuthor
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
    PostSerializer,
    UserRegisterSerializer,
    PostSummarySerializer,
    TagSerializer,
    CommentSerializer,
)
from django.contrib.auth import get_user_model
from .models import Profile, Post, Category, Tag, Comment
from django.db.models import F, Q, Count, DateTimeField, ExpressionWrapper
from django.utils import timezone
import json
from datetime import date, datetime, timedelta
import random

User = get_user_model()
# Create your views here.


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        try:
            user = authenticate(
                username=request.data["username"], password=request.data["password"]
            )
            if user is not None:
                refresh = self.get_serializer(data=request.data)
                refresh.is_valid(raise_exception=True)
                data = refresh.validated_data
                data["user"] = UserSerializer(user).data
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "error login"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": "error login"}, status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            username = data.get("email")
            password = data.get("password")
            email = data.get("email")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            gender = data.get("gender")
            profile_pic = data.get("profile_pic")

            user = User.objects.filter(username=username).first()
            if user is None:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.groups.add(2)
                user.save()

                profile = Profile.objects.create(
                    user=user,
                    email=email,
                    profile_pic=profile_pic,
                    gender=gender,
                )

                profile.save()
                serializer = UserSerializer(user)

                refresh = self.get_serializer(
                    data={"username": username, "password": password}
                )

                try:
                    refresh.is_valid(raise_exception=True)
                    data = refresh.validated_data
                    data["user"] = serializer.data
                    return Response(data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"error": "error register"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TestView(APIView):
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (JWTAuthentication,)

    # def get(self, request, *args, **kwargs):
    #     try:
    #         Post.objects.all().update( created_at=ExpressionWrapper(F('created_at') - timedelta(hours=7), output_field=DateTimeField()))
    #         Comment.objects.all().update( created_at=ExpressionWrapper(F('created_at') - timedelta(hours=7), output_field=DateTimeField()))
    #         Tag.objects.all().update( created_at=ExpressionWrapper(F('created_at') - timedelta(hours=7), output_field=DateTimeField()))
    #         return Response({"message": "Hello World! This is a test view."}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            refresh = request.data.get("refresh_token")
            data = {"message": "Hello World! This is a test view.", "refresh": refresh}
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostView(APIView):
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            posts = Post.objects.all()
            serializer = PostSummarySerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            user_id = request.user.id
            title = data.get("title")
            sapo = data.get("sapo")
            body = data.get("body")
            tags = json.loads(data.get("tags"))
            thumbnail = data.get("thumbnail")
            main_category = data.get("main_category")
            sub_category = data.get("sub_category")

            category, created = Category.objects.get_or_create(
                main_category=main_category, sub_category=sub_category
            )

            post = Post.objects.create(
                user_id=user_id,
                title=title,
                sapo=sapo,
                body=body,
                thumbnail=thumbnail,
                category=category,
            )
            post.save()

            for tag in tags:
                tag, created = Tag.objects.get_or_create(tag_name=tag)
                tag.tag_count = F("tag_count") + 1
                tag.save()
                post.tags.add(tag)
            post.save()
            serializer = PostSerializer(post)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        try:
            post_id = kwargs.get("post_id")
            post = Post.objects.get(id=post_id)
            post.view_count += 1
            post.save()
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            post_id = kwargs.get("post_id")
            post = Post.objects.get(id=post_id)

            if request.user.is_staff or request.user.id == post.user_id:
                post.title = data.get("title")
                post.sapo = data.get("sapo")
                post.body = data.get("body")
                if type(data.get("thumbnail")) == str:
                    post.thumbnail = data.get("thumbnail").replace(
                        "http://127.0.0.1:8000/media/", ""
                    )
                else:
                    post.thumbnail = data.get("thumbnail")
                post.category.main_category = data.get("main_category")
                post.category.sub_category = data.get("sub_category")
                post.category.save()
                post.save()
                tags = json.loads(data.get("tags"))
                tags_old = post.tags.all()
                for tag in tags_old:
                    tag.tag_count = F("tag_count") - 1
                    tag.save()
                post.tags.clear()
                for tag in tags:
                    tag, created = Tag.objects.get_or_create(tag_name=tag)
                    tag.tag_count = F("tag_count") + 1
                    tag.save()
                    post.tags.add(tag)

                post.save()
                serializer = PostSerializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "You don't have permission to edit this post"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            post_id = kwargs.get("post_id")
            post = Post.objects.get(id=post_id)
            if request.user.is_staff or request.user.id == post.user_id:
                tags = post.tags.all()
                for tag in tags:
                    tag.tag_count = F("tag_count") - 1
                    tag.save()
                post.delete()
                return Response(
                    {"message": "Delete success"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "You don't have permission to delete this post"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostByAuthorView(APIView):
    permission_classes = (IsAdminOrAuthor,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            index = request.GET.get("index")
            count = request.GET.get("count")
            if not index:
                index = 0
            else:
                index = int(index)
            if not count:
                count = 10
            else:
                count = int(count)
            posts = Post.objects.order_by("-created_at").filter(user_id=user_id)
            number_of_posts = posts.count()
            posts = posts[index : index + count]
            serializer = PostSummarySerializer(posts, many=True)
            return Response(
                {"number_of_posts": number_of_posts, "posts": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostByUserView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            id = kwargs.get("author_id")
            author = User.objects.get(id=id)
            if not author:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST
                )
            author_serializer = UserSerializer(author)
            author_id = author.id
            index = request.GET.get("index")
            count = request.GET.get("count")
            if not index:
                index = 0
            else:
                index = int(index)
            if not count:
                count = 10
            else:
                count = int(count)
            posts = Post.objects.order_by("-view_count").filter(user_id=author_id)
            number_of_posts = posts.count()
            posts = posts[index : index + count]
            serializer = PostSummarySerializer(posts, many=True)

            return Response(
                {
                    "author": author_serializer.data,
                    "number_of_posts": number_of_posts,
                    "posts": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostByCategoryView(APIView):
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            main_category = request.GET.get("main_category")
            sub_category = request.GET.get("sub_category")
            index = request.GET.get("index")
            count = request.GET.get("count")
            filter = request.GET.get("filter_by")
            if not index:
                index = 0
            else:
                index = int(index)
            if not count:
                count = 10
            else:
                count = int(count)

            if filter == "view":
                if not main_category:
                    posts = Post.objects.order_by("-view_count")[index : index + count]
                elif not sub_category:
                    posts = Post.objects.order_by("-view_count").filter(
                        category__main_category__iexact=main_category
                    )[index : index + count]
                else:
                    posts = Post.objects.order_by("-view_count").filter(
                        category__main_category__iexact=main_category,
                        category__sub_category__iexact=sub_category,
                    )[index : index + count]

            elif filter == "today":
                today = timezone.now().date()
                if not main_category:
                    posts = Post.objects.filter(
                        created_at__month=today.month,
                        created_at__year=today.year,
                    )
                elif not sub_category:
                    posts = Post.objects.filter(
                        created_at__month=today.month,
                        created_at__year=today.year,
                        category__main_category__iexact=main_category,
                    )
                else:
                    posts = Post.objects.filter(
                        created_at__month=today.month,
                        created_at__year=today.year,
                        category__main_category__iexact=main_category,
                        category__sub_category__iexact=sub_category,
                    )
                post_list = list(posts)
                random.shuffle(post_list)
                posts = post_list[index : index + count]

            elif filter == "month":
                today = timezone.now().date()
                print(today.day, today.month, today.year)
                if not main_category:
                    posts = Post.objects.filter(
                        created_at__year=today.year,
                        created_at__month=today.month,
                    ).order_by("-view_count")
                elif not sub_category:
                    posts = Post.objects.filter(
                        created_at__year=today.year,
                        created_at__month=today.month,
                        category__main_category__iexact=main_category,
                    ).order_by("-view_count")
                else:
                    posts = Post.objects.filter(
                        created_at__year=today.year,
                        created_at__month=today.month,
                        category__main_category__iexact=main_category,
                        category__sub_category__iexact=sub_category,
                    ).order_by("-view_count")

                post_list = list(posts)
                posts = post_list[index : index + count]

            else:
                if not main_category:
                    posts = Post.objects.order_by("-created_at")[index : index + count]
                elif not sub_category:
                    print(main_category + " " + str(index) + " " + str(count))
                    posts = Post.objects.order_by("-created_at").filter(
                        category__main_category__iexact=main_category
                    )[index : index + count]
                else:
                    posts = Post.objects.order_by("-created_at").filter(
                        category__main_category__iexact=main_category,
                        category__sub_category__iexact=sub_category,
                    )[index : index + count]

            serializer = PostSummarySerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostByTagView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            tag_name = request.GET.get("tag_name", "").split(",")
            index = request.GET.get("index")
            count = request.GET.get("count")
            filter = request.GET.get("filter_by")
            q_objects = Q()
            for tag in tag_name:
                q_objects |= Q(tags__tag_name__iexact=tag)
            if not index:
                index = 0
            else:
                index = int(index)
            if not count:
                count = 10
            else:
                count = int(count)
            if not filter or filter == "latest":
                posts = Post.objects.order_by("-created_at").filter(q_objects)[
                    index : index + count
                ]
            if filter == "trending":
                today = timezone.now().date()
                tag_trending = Tag.objects.order_by("-tag_count").filter(
                    created_at__year=today.year,
                    created_at__month=today.month,
                )[index : index + count]

                serializer = TagSerializer(tag_trending, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                posts = Post.objects.order_by("created_at").filter(q_objects)[
                    index : index + count
                ]

            serializer = PostSummarySerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            q = request.GET.get("q")
            filter = request.GET.get("filter")
            type = request.GET.get("type")
            index = request.GET.get("index")
            count = request.GET.get("count")
            posts = Post.objects.none()
            if not index:
                index = 0
            else:
                index = int(index)
            if not count:
                count = 10
            else:
                count = int(count)

            if not filter or filter == "1":
                if not type or type == "1":
                    posts = (
                        Post.objects.order_by("-created_at")
                        .filter(Q(tags__tag_name__icontains=q) | Q(title__icontains=q))
                        .distinct()[index : index + count]
                    )
                elif type == "2":
                    posts = (
                        Post.objects.order_by("created_at")
                        .filter(Q(title__icontains=q) | Q(tags__tag_name__icontains=q))
                        .distinct()[index : index + count]
                    )
                elif type == "3":
                    posts = (
                        Post.objects.order_by("-view_count")
                        .filter(Q(title__icontains=q) | Q(tags__tag_name__icontains=q))
                        .distinct()[index : index + count]
                    )

            elif filter == "2":
                keys_list = q.split(" ")
                query = Q()
                for key in keys_list:
                    query &= Q(user__first_name__icontains=key) | Q(
                        user__last_name__icontains=key
                    )
                if not type or type == "1":
                    posts = Post.objects.order_by("-created_at").filter(query)[
                        index : index + count
                    ]
                elif type == "2":
                    posts = Post.objects.order_by("created_at").filter(query)[
                        index : index + count
                    ]
                elif type == "3":
                    posts = Post.objects.order_by("-view_count").filter(query)[
                        index : index + count
                    ]
            serializer = PostSummarySerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CommentView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        try:
            post_id = kwargs.get("post_id")
            index = request.GET.get("index")
            count = request.GET.get("count")
            filter = request.GET.get("filter_by")
            if not index:
                index = 0
            else:
                index = int(index)
            if not count:
                count = 3
            else:
                count = int(count)

            def build_comment_tree(comment):
                children = list(comment.get_children())
                comment = CommentSerializer(
                    comment, context={"user": request.user}
                ).data
                if not children:
                    return comment
                comment["children"] = [build_comment_tree(child) for child in children]
                return comment

            if not filter or filter == "2":
                comments = Comment.objects.filter(
                    post_id=post_id, parent_id=None
                ).order_by("-created_at")[index : index + count]

            elif filter == "1":
                comments = (
                    Comment.objects.filter(post_id=post_id, parent_id=None)
                    .annotate(like_count=Count("user_like"))
                    .order_by("-like_count", "-created_at")[index : index + count]
                )
            comments = [build_comment_tree(comment) for comment in comments]
            comments_count = Comment.objects.filter(post_id=post_id).count()
            return Response(
                {"comments": comments, "comments_count": comments_count},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            post_id = kwargs.get("post_id")
            content = data.get("content")
            parent_id = data.get("parent_id")
            post = Post.objects.get(id=post_id)
            if parent_id is not None:
                parent = Comment.objects.get(id=parent_id)
                comment = Comment.objects.create(
                    user=user,
                    post=post,
                    content=content,
                    parent=parent,
                )
            else:
                comment = Comment.objects.create(
                    user=user,
                    post=post,
                    content=content,
                )
            comment.save()
            serializer = CommentSerializer(comment, context={"user": request.user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LikeCommentView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            comment_id = kwargs.get("comment_id")
            comment = Comment.objects.get(id=comment_id)
            if user in comment.user_like.all():
                comment.user_like.remove(user)
                print("unlike")
            else:
                comment.user_like.add(user)
                print("like")
            comment.save()
            serializer = CommentSerializer(comment, context={"user": request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
