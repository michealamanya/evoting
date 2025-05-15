from django.shortcuts import render

def about(request):
    return render(request, 'pages/about.html')

def how_it_works(request):
    return render(request, 'pages/how_it_works.html')

def faq(request):
    return render(request, 'pages/faq.html')

def blog(request):
    # Handle pagination
    page = request.GET.get('page', 1)
    category = request.GET.get('category', 'all')
    
    # In a real app, you would query the database
    # For now, we'll simulate pagination with the template
    
    return render(request, 'pages/blog.html', {
        'page': int(page),
        'category': category
    })

def blog_post(request, post_id):
    # In a real app, you would fetch the post by ID
    # For now, we'll simulate a post with placeholder data
    
    post = {
        'id': post_id,
        'title': 'The Future of E-Voting Security',
        'author': 'Tech Team',
        'date': 'May 10, 2025',
        'category': 'Security',
        'views': 1243,
        'comments': 3,
        # In a real app, you would have the actual content here
    }
    
    return render(request, 'pages/blog_post.html', {'post': post})

def contact(request):
    return render(request, 'pages/contact.html')
