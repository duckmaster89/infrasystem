from django.urls import path
from . import views

urlpatterns = [
    # URLs principales
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('menu/', views.menu, name='menu'),
    path('signout/', views.signout, name='signout'),
    path('signin/', views.signin, name='signin'),
    path('submenu_crear/', views.submenu_crear, name='submenu_crear'),
    path('submenu_listar/', views.submenu_listar, name='submenu_listar'),
    
    # URLs para ambientes
    path('create/ambiente/', views.create_ambiente, name='create_ambiente'),
    path('list/ambiente/', views.list_ambiente, name='list_ambiente'),
    path('edit/ambiente/<int:ambiente_id>/', views.edit_ambiente, name='edit_ambiente'),
    path('delete/ambiente/<int:ambiente_id>/', views.delete_ambiente, name='delete_ambiente'),
    
    # URLs para usuarios
    path('list/users/', views.list_users, name='list_users'),
    path('create/user/', views.create_user, name='create_user'),
    path('edit/user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete/user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # URLs para perfiles
    path('create/perfil/', views.create_perfil, name='create_perfil'),
    path('list/perfiles/', views.list_perfiles, name='list_perfiles'),
    path('edit/perfil/<int:perfil_id>/', views.edit_perfil, name='edit_perfil'),
    path('delete/perfil/<int:perfil_id>/', views.delete_perfil, name='delete_perfil'),

    # URLs para clouds
    path('create/cloud/', views.create_cloud, name='create_cloud'),
    path('list/clouds/', views.list_clouds, name='list_clouds'),
    path('edit/cloud/<int:cloud_id>/', views.edit_cloud, name='edit_cloud'),
    path('delete/cloud/<int:cloud_id>/', views.delete_cloud, name='delete_cloud'),

    # URLs para solicitantes
    path('create/solicitante/', views.create_solicitante, name='create_solicitante'),
    path('list/solicitantes/', views.list_solicitantes, name='list_solicitantes'),
    path('edit/solicitante/<int:solicitante_id>/', views.edit_solicitante, name='edit_solicitante'),
    path('delete/solicitante/<int:solicitante_id>/', views.delete_solicitante, name='delete_solicitante'),
    
    # URLs para gerencias
    path('create/gerencia/', views.create_gerencia, name='create_gerencia'),
    
    # URLs para puestos
    path('create/puesto/', views.create_puesto, name='create_puesto'),
] 