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
    path('list/gerencias/', views.list_gerencias, name='list_gerencias'),
    path('edit/gerencia/<int:gerencia_id>/', views.edit_gerencia, name='edit_gerencia'),
    path('delete/gerencia/<int:gerencia_id>/', views.delete_gerencia, name='delete_gerencia'),
    
    # URLs para puestos
    path('create/puesto/', views.create_puesto, name='create_puesto'),
    path('list/puestos/', views.list_puestos, name='list_puestos'),
    path('edit/puesto/<int:puesto_id>/', views.edit_puesto, name='edit_puesto'),
    path('delete/puesto/<int:puesto_id>/', views.delete_puesto, name='delete_puesto'),

    # URLs para proyectos
    path('create/proyecto/', views.create_proyecto, name='create_proyecto'),
    path('list/proyectos/', views.list_proyectos, name='list_proyectos'),
    path('edit/proyecto/<int:proyecto_id>/', views.edit_proyecto, name='edit_proyecto'),
    path('delete/proyecto/<int:proyecto_id>/', views.delete_proyecto, name='delete_proyecto'),

    # URLs para estados de proyecto
    path('create/status_proyecto/', views.create_status_proyecto, name='create_status_proyecto'),
    path('list/status_proyectos/', views.list_status_proyectos, name='list_status_proyectos'),
    path('edit/status_proyecto/<int:status_id>/', views.edit_status_proyecto, name='edit_status_proyecto'),
    path('delete/status_proyecto/<int:status_id>/', views.delete_status_proyecto, name='delete_status_proyecto'),

    # URLs para VLANs
    path('create/vlan/', views.create_vlan, name='create_vlan'),
    path('list/vlans/', views.list_vlans, name='list_vlans'),
    path('edit/vlan/<int:vlan_id>/', views.edit_vlan, name='edit_vlan'),
    path('delete/vlan/<int:vlan_id>/', views.delete_vlan, name='delete_vlan'),

    # URLs para países
    path('create/pais/', views.create_pais, name='create_pais'),
    path('list/paises/', views.list_paises, name='list_paises'),
    path('edit/pais/<int:pais_id>/', views.edit_pais, name='edit_pais'),
    path('delete/pais/<int:pais_id>/', views.delete_pais, name='delete_pais'),

    # URLs para redes
    path('create/red/', views.create_red, name='create_red'),
    path('list/redes/', views.list_redes, name='list_redes'),
    path('edit/red/<int:red_id>/', views.edit_red, name='edit_red'),
    path('delete/red/<int:red_id>/', views.delete_red, name='delete_red'),

    # URLs para usos de red
    path('create/uso_red/', views.create_uso_red, name='create_uso_red'),
    path('list/usos_red/', views.list_usos_red, name='list_usos_red'),
    path('edit/uso_red/<int:uso_id>/', views.edit_uso_red, name='edit_uso_red'),
    path('delete/uso_red/<int:uso_id>/', views.delete_uso_red, name='delete_uso_red'),
    path('usos-red/get-proyectos/<int:uso_red_id>/', views.get_proyectos_by_uso_red, name='get_proyectos_by_uso_red'),

    # URLs para CPU
    path('create/cpu/', views.create_cpu, name='create_cpu'),
    path('list/cpus/', views.list_cpus, name='list_cpus'),
    path('edit/cpu/<int:cpu_id>/', views.edit_cpu, name='edit_cpu'),
    path('delete/cpu/<int:cpu_id>/', views.delete_cpu, name='delete_cpu'),

    # URLs para VTI
    path('vtis/', views.list_vtis, name='list_vtis'),
    path('vtis/create/', views.create_vti, name='create_vti'),
    path('vtis/<int:vti_id>/edit/', views.edit_vti, name='edit_vti'),
    path('vtis/<int:vti_id>/delete/', views.delete_vti, name='delete_vti'),
] 