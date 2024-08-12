from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, PostForm, CommentForm, BioForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Profile, User, Like
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum
from datetime import datetime
# Create your views here.

@login_required(login_url="/login")
def home(request):
    #Profile.objects.all().delete()
    #Comment.objects.all().delete()

    if request.method == "POST":
        if "post-id" in request.POST:
            post_id = request.POST.get("post-id")
            post = Post.objects.filter(id=post_id).first()
            if post and post.author == request.user:
                post.delete()


    profile = Profile.objects.filter(author=request.user).first()

    # Order the posts by newest first
    posts = Post.objects.annotate(like_count=Count('like')).order_by('-like_count', '-created_at')

    return render(request, 'main/home.html', {'posts':posts,'profile':profile})

@login_required(login_url="/login")
def like_post(request):
    post_id = request.POST.get("post_id")
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    like = Like.objects.filter(author=user, post=post)
    if like:
        like.delete()
        liked = False
    else:
        like = Like(author=user, post=post)
        like.save()
        liked = True

    like_count = post.like_set.count()
    return JsonResponse({'liked': liked, 'like_count': like_count})


def sign_up(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST) # this connects to the form we made
        if form.is_valid():
            user = form.save()
            login(request, user)
            profile = Profile(author=user, bio='Add a bio here')
            profile.save()
            return redirect('/home')
    else:
        form = RegistrationForm()

    return render(request, 'registration/sign_up.html',  {'form':form})

#@login_required(login_url="/login")
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    else:
        logout(request)
        return render(request, 'registration/loggedout.html')

@login_required(login_url="/login")
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            profile = Profile.objects.filter(author=request.user).first()
            profile.posts.add(post)
            profile.save()
            return redirect('/home')
    else:
        form = PostForm()

    return render(request, "main/create_post.html", {'form':form})


@login_required(login_url="/login")
def post_view(request, id):
    post = Post.objects.filter(id=id).first()
    # workout if post == None
    if request.method == "POST":
        if 'post-id' in request.POST:
            post_id = request.POST.get("post-id")
            if post and post.author == request.user:
                post.delete()
            return redirect('/home')
        elif 'comment-id' in request.POST:
            comment_id = request.POST.get("comment-id")
            comment = Comment.objects.filter(id=comment_id).first()
            if comment and comment.author == request.user:
                comment.delete()
            return redirect(f'/{id}')
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(f'/{id}')
    else:
        form = CommentForm()
        comments = post.comments.all()

    return render(request, "main/post_view.html", {'post':post, 'form':form, 'comments':comments})

@login_required(login_url="/login")
def change_bio(request):
    if request.method == 'POST':
        profile = Profile.objects.filter(author=request.user).first()
        form = BioForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
        return HttpResponse(profile.bio)
    return HttpResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url="/login")
def profile_view(request, name):
    # If a POST:
    if request.method == "POST":
        request_profile = Profile.objects.filter(author=request.user).first()
        action_profile = Profile.objects.filter(author=User.objects.filter(username=name).first()).first()
        # 1) unfollow them, or
        if "unfollow-user" in request.POST:
            request_profile.following.remove(action_profile.author)
            action_profile.followers.remove(request_profile.author)
        # 2) begin following them
        elif "follow-user" in request.POST:
            request_profile.following.add(action_profile.author)
            action_profile.followers.add(request_profile.author)
        elif 'post-id' in request.POST:
            post_id = request.POST.get("post-id")
            post = Post.objects.filter(id=post_id).first()
            if post and post.author == request.user:
                post.delete()

        redirect(f'/profile/{name}')

    ### END POST ###

    # If not a POST, return the specified user's profile
    queried_user = User.objects.filter(username=name).first()
    profile = Profile.objects.filter(author=queried_user).first()

    # If the user doesn't exist return empty page
    if queried_user is None:
        return render(request, 'main/profile_view.html', {'profile': None, 'posts': None})

    # If we search a user who exists but doesn't have a setup profile, add it for them
    if profile is None and queried_user is not None:
        profile = Profile(author=queried_user, bio='Add a bio here')
        profile.save()
        queried_posts = Post.objects.filter(author=queried_user).all()
        for post in queried_posts:
            profile.posts.add(post)
        profile.save()

    posts = profile.posts.all()
    form = BioForm()

    # Get the total number of likes across all Like objects for every Post the User has
    total_likes = Post.objects.filter(author=queried_user).annotate(like_count=Count('like')).aggregate(total_likes=Sum('like_count'))['total_likes'] or 0

    return render(request, 'main/profile_view.html', {'profile':profile, 'posts':posts, 'form':form, 'total_likes':total_likes})