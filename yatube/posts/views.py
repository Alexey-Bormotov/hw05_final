from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()

SHOW_POSTS = 10


def index(request):
    template = 'posts/index.html'
    posts_all = Post.objects.all()

    paginator = Paginator(posts_all, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_all = group.posts.all()

    paginator = Paginator(posts_all, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_all = author.posts.all()
    posts_count = author.posts.count()
    following = False

    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()

    paginator = Paginator(posts_all, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'posts_count': posts_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    form = CommentForm()
    comments = post.comments.all()

    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if request.method == 'POST':

        if form.is_valid():
            post_temp = form.save(commit=False)
            post_temp.author = request.user
            post_temp.save()
            return redirect('posts:profile', username=request.user.username)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('/posts/' + str(post_id))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if request.method == 'POST':

        if form.is_valid():
            form.save()
            return redirect('/posts/' + str(post_id))

    return render(request, 'posts/create_post.html', {
        'form': form,
        'post_id': post_id,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment_temp = form.save(commit=False)
        comment_temp.author = request.user
        comment_temp.post = post
        comment_temp.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    fav_authors = request.user.follower.all()
    fav_authors_list = [fav_author.author for fav_author in fav_authors]

    fav_posts = Post.objects.filter(author__in=fav_authors_list)

    paginator = Paginator(fav_posts, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if request.user != author:
        if not Follow.objects.filter(
            user=request.user,
            author=author
        ).exists():
            Follow.objects.create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()

    return redirect('posts:profile', username=username)
