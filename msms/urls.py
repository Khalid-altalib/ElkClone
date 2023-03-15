"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('sign_up', views.sign_up, name='sign_up'),
    path('log_in', views.log_in, name='log_in'),
    path('log_out', views.log_out, name='log_out'),
    # Path to the user's initial home page
    path('home/', views.user_home, name="user_home"),
    # Path to the make request form
    path('make_request/', views.make_request, name="make_request"),
    # Path to the edit request form
    path('edit/<int:requestId>', views.edit_request, name="edit_request"),
    # Path to see more of requests
    path('see_more/<int:requestId>', views.see_more_request, name="see_more_request"),
    # Path to the administrator's initial home page
    path('administrator/', views.admin_home, name="admin_home"),
    # Path to administrator's side of approving requests
    path('approve/<int:requestId>/', views.approve_request, name='approve'),  # name='approve_request'),
    # Path to administrator's side of deleting requests
    # path('deleteRequest/<int:requestId>/', views.deleteRequest, name='delete_request'), # LYN's VERSION
    # Path to  delete requests
    path('delete/<int:requestId>/', views.delete_request, name='delete'),
    # Path to administrator's side of deleting invoices
    path('deleteInvoice/<int:invoiceId>/', views.deleteInvoice, name='delete_invoice'),
    # Path to the create transaction form
    path('create_transaction/', views.create_transaction, name="create_transaction"),
    path('director/', views.director_home, name="director_home"),
    path('edit_user/<int:user_id>/', views.edit_user, name="edit_user"),
    path('delete_user/<int:user_id>/', views.delete_user, name="delete_user"),
    path('view_student/<int:user_id>/', views.view_student, name="view_student"),
    path('register_child/', views.register_child, name="register_child"),
    path('edit_child/<int:child_id>/', views.edit_child, name="edit_child"),
    path('delete_child/<int:child_id>/', views.delete_child, name="delete_child")
]
