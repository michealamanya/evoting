from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog, name='blog'),
    path('blog/post/<int:post_id>/', views.blog_post, name='blog_post'),
    path('contact/', views.contact, name='contact'),
]
