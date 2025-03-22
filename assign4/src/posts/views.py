from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Post, Photo
from .forms import PostForm
from profiles.models import Profile
from .utils import action_permission
from django.contrib.auth.decorators import login_required
from django.db.models import Count
@login_required
def post_list_and_create(request):
    form = PostForm(request.POST or None)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if form.is_valid():
            author = Profile.objects.get(user=request.user)
            instance = form.save(commit=False)
            instance.author = author
            instance.save()
            return JsonResponse({
                'title': instance.title,
                'description': instance.description,
                'author': instance.author.user.username,
                'id': instance.id,
            })
    context = {'form': form}
    return render(request, 'posts/main.html', context)

@login_required
def post_detail(request, pk):
    obj = Post.objects.get(pk=pk)
    form = PostForm()
    context = {'obj': obj, 'form': form}
    return render(request, 'posts/detail.html', context)

from django.db.models import Count

@login_required
def load_post_data_view(request, num_posts):
    visible = 3
    upper = num_posts
    lower = upper - visible
    size = Post.objects.all().count()

    sort = request.GET.get('sort', 'updated')

    if sort == 'likes':
        qs = Post.objects.annotate(like_total=Count('liked')).order_by('-like_total', '-updated')
    elif sort == 'oldest':
        qs = Post.objects.order_by('created')
    else:
        qs = Post.objects.order_by('-updated')

    data = []
    for obj in qs:
        item = {
            'id': obj.id,
            'title': obj.title,
            'description': obj.description,
            'liked': request.user in obj.liked.all(),
            'count': obj.like_total if sort == 'likes' else obj.liked.count(),
            'author': obj.author.user.username,
        }
        data.append(item)

    return JsonResponse({'data': data[lower:upper], 'size': size})


@login_required
def post_detail_data_view(request, pk):
    obj = Post.objects.get(pk=pk)
    data = {
        'id': obj.id,
        'title': obj.title,
        'description': obj.description,
        'author': obj.author.user.username,
        'logged_in': request.user.username,
    }
    return JsonResponse({'data': data})

@login_required
def like_unlike_post(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        pk = request.POST.get('pk')
        obj = Post.objects.get(pk=pk)
        if request.user in obj.liked.all():
            liked = False
            obj.liked.remove(request.user)
        else:
            liked = True
            obj.liked.add(request.user)
        return JsonResponse({'liked': liked, 'count': obj.liked.count()})
    
    return redirect('posts:main-page')

@login_required
@action_permission
def update_post(request, pk):
    obj = Post.objects.get(pk=pk)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        new_title = request.POST.get('title')
        new_description = request.POST.get('description')

        if not new_title or not new_description:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        obj.title = new_title
        obj.description = new_description
        obj.save()

        return JsonResponse({'title': new_title, 'description': new_description})
    
    return redirect('posts:main-page')

@login_required
@action_permission
def delete_post(request, pk):
    obj = Post.objects.get(pk=pk)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        obj.delete()
        return JsonResponse({'message': 'Post deleted successfully!'})
    
    return redirect('posts:main-page')

@login_required
def image_upload_view(request):
    if request.method == 'POST':
        img = request.FILES.get('file')
        new_post_id = request.POST.get('new_post_id')

        if img and new_post_id:
            try:
                post = Post.objects.get(id=new_post_id)
                Photo.objects.create(image=img, post=post)

                return JsonResponse({'message': 'Image uploaded successfully!'})
            except Post.DoesNotExist:
                return JsonResponse({'error': 'Post not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)
