from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    TestView,
    MyTokenObtainPairView,
    LogoutView,
    RegisterView,
    PostView,
    PostDetailView,
    PostByUserView,
    PostByCategoryView,
    PostByTagView,
    PostByAuthorView,
    SearchView,
    CommentView,
    LikeCommentView,
)

urlpatterns = [
    path("hello/", TestView.as_view(), name="test"),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("posts/", PostView.as_view(), name="post"),
    path("posts/<uuid:post_id>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/category/", PostByCategoryView.as_view(), name="post_by_category"),
    path("posts/tag/", PostByTagView.as_view(), name="post_by_tag"),
    path("posts/author/<int:author_id>/", PostByUserView.as_view(), name="post_by_user"),
    path("posts/author/", PostByAuthorView.as_view(), name="post_by_user"),
    path("search/", SearchView.as_view(), name="post_by_user"),
    path("comments/<uuid:post_id>/", CommentView.as_view(), name="comment"),
    path("comments/like/<int:comment_id>/", LikeCommentView.as_view(), name="like_comment"),
]   
