from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Post, Profile, Comment
from .forms import PostForm, CommentForm, ProfileUpdateForm
from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('profile', username=username) 
    else:
        form = UserRegistrationForm()
    return render(request, 'social_app/register.html', {'form': form})

def search_user(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = User.objects.filter(username__icontains=query)  # Case-insensitive search for usernames

    return render(request, 'social_app/base.html', {'results': results, 'query': query})


class PostListView(ListView):
    model = Post
    template_name = 'social_app/home.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10

    def get_queryset(self):
        # Ensure the user is authenticated before filtering by followers
        if self.request.user.is_authenticated:
            return Post.objects.filter(author__profile__followers=self.request.user.profile).order_by('-created_at')
        return Post.objects.none()  # Return an empty queryset for unauthenticated users

class PostDetailView(DetailView):
    model = Post
    template_name = 'social_app/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'social_app/post_forms.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'social_app/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': post.likes.count()})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('post-detail', pk=pk)

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social_app/post_confirm_delete.html'
    success_url = reverse_lazy('home')  # Redirect to home after deletion

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'social_app/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        
        # Safely access posts only if the user is authenticated or the profile belongs to the logged-in user.
        if self.request.user.is_authenticated and self.request.user == user:
            context['posts'] = Post.objects.filter(author=user).order_by('-created_at')
        else:
            context['posts'] = []  # No posts to show for unauthenticated users
        
        return context

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'social_app/profile_update.html', {'form': form})

@login_required
def follow_toggle(request, username):
    user_to_toggle = get_object_or_404(User, username=username)
    
    # Check if the current user's profile is already following the target user's profile.
    if request.user.profile in user_to_toggle.profile.followers.all():
        request.user.profile.following.remove(user_to_toggle.profile)
        is_following = False
    else:
        request.user.profile.following.add(user_to_toggle.profile)
        is_following = True
    
    return JsonResponse({'is_following': is_following})

class ExploreView(ListView):
    model = Post
    template_name = 'social_app/explore.html'
    context_object_name = 'posts'
    paginate_by = 15

    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')
    
def profile_redirect(request):
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    return redirect('login')