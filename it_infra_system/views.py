from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .forms import AmbienteForm, SolicitanteForm, GerenciaForm, PuestoForm, VLANForm, ProyectoForm, StatusProyectoForm, PaisForm, REDForm, UsoRedForm, CPUForm, VTIForm
from .models import AMBIENTE, Bitacora, Perfil, UsuarioExtendido, CLOUD, SOLICITANTE, GERENCIA, PUESTO, VLAN, PROYECTO, STATUS_PROYECTO, PAIS, RED, USO_RED, CONTROL_VLAN, VLAN_IP, CPU, VTI
from django.contrib import messages
from .decorators import custom_login_required
from django.http import JsonResponse
import ipaddress
from django.db import connection


# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            email = request.POST.get('email', '')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')

            # Validaciones básicas
            if not username or not password1 or not password2:
                return render(request, 'signup.html', {'error': 'Los campos obligatorios deben estar completos'})
            
            if password1 != password2:
                return render(request, 'signup.html', {'error': 'Las contraseñas no coinciden'})
            
            if User.objects.filter(username=username).exists():
                return render(request, 'signup.html', {'error': 'El nombre de usuario ya existe'})

            # Crear usuario
            user = User.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Crear usuario extendido sin perfiles asignados
            UsuarioExtendido.objects.create(user=user)

            messages.success(request, 'Usuario creado exitosamente. Por favor, espere a que un administrador le asigne los perfiles correspondientes.')
            return redirect('signin')

        except Exception as e:
            return render(request, 'signup.html', {'error': f'Error al crear usuario: {str(e)}'})

    return render(request, 'signup.html')


@custom_login_required
def menu(request):
    return render(request, 'menu.html')


def signout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('menu')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar si el usuario tiene al menos un perfil asignado
            try:
                usuario_extendido = UsuarioExtendido.objects.get(user=user)
                if not usuario_extendido.perfiles.exists():
                    messages.error(request, 'No tiene perfiles asignados. Por favor, contacte al administrador.')
                    return render(request, 'signin.html', {'error': 'No tiene perfiles asignados'})
                
                login(request, user)
                return redirect('menu')
            except UsuarioExtendido.DoesNotExist:
                messages.error(request, 'Error con su cuenta de usuario. Por favor, contacte al administrador.')
                return render(request, 'signin.html', {'error': 'Error con su cuenta de usuario'})
        else:
            return render(request, 'signin.html', {'error': 'Usuario o contraseña incorrectos'})
    
    return render(request, 'signin.html')

#para formularios#        
def registrar_evento(usuario, tipo_accion, tabla, descripcion):
    Bitacora.objects.create(
        usuario=usuario,
        tipo_accion=tipo_accion,
        tabla_afectada=tabla,
        descripcion=descripcion
    )

@custom_login_required
def create_ambiente(request):
    if request.method == 'GET':
        return render(request, 'create_ambiente.html', {
            'form': AmbienteForm
        })
    else:
        try:
            form = AmbienteForm(request.POST)
            nuevo_ambiente = form.save(commit=False)
            
            # Encontrar el ID más pequeño disponible
            ids_existentes = set(AMBIENTE.objects.values_list('id_ambiente', flat=True))
            id_nuevo = 1
            while id_nuevo in ids_existentes:
                id_nuevo += 1
            
            nuevo_ambiente.id_ambiente = id_nuevo
            nuevo_ambiente.user_create = request.user
            nuevo_ambiente.fecha_creacion = timezone.now()
            nuevo_ambiente.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'CREATE',
                'AMBIENTE',
                f'Creación de ambiente: {nuevo_ambiente.nombre_ambiente}'
            )
            
            return redirect('list_ambiente')
        except ValueError:
            return render(request, 'create_ambiente.html', {
                'form': AmbienteForm,
                'error': 'Por favor proporcione datos válidos'
            })

#para listar datos#
@custom_login_required
def list_ambiente(request):
    ambientes = AMBIENTE.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'AMBIENTE',
        'Visualización de lista de ambientes'
    )
    
    return render(request, 'list_ambiente.html', {'list_ambiente': ambientes})

@custom_login_required
def submenu_crear(request):
    messages_list = list(messages.get_messages(request))
    return render(request, 'submenu_crear.html', {
        'messages': messages_list
    })

@custom_login_required
def submenu_listar(request):
    return render(request, 'submenu_listar.html')

@custom_login_required
def edit_ambiente(request, ambiente_id):
    ambiente = get_object_or_404(AMBIENTE, id_ambiente=ambiente_id)

    if request.method == 'GET':
        return render(request, 'edit_ambiente.html', {
            'ambiente': ambiente
        })
    else:
        try:
            ambiente.nombre_ambiente = request.POST['nombre_ambiente']
            ambiente.descripcion_ambiente = request.POST['descripcion_ambiente']
            ambiente.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'AMBIENTE',
                f'Actualización de ambiente: {ambiente.nombre_ambiente}'
            )
            
            return redirect('list_ambiente')
        except ValueError:
            return render(request, 'edit_ambiente.html', {
                'ambiente': ambiente,
                'error': 'Error actualizando el ambiente'
            })

@custom_login_required
def delete_ambiente(request, ambiente_id):
    ambiente = get_object_or_404(AMBIENTE, id_ambiente=ambiente_id)
    nombre_ambiente = ambiente.nombre_ambiente
    ambiente.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'AMBIENTE',
        f'Eliminación de ambiente: {nombre_ambiente}'
    )
    
    return redirect('list_ambiente')

@custom_login_required
def list_users(request):
    try:
        # Obtener el perfil del usuario actual y verificar si es administrador
        try:
            usuario_extendido = UsuarioExtendido.objects.get(user=request.user)
            es_administrador = usuario_extendido.es_administrador()
        except UsuarioExtendido.DoesNotExist:
            print("Error: UsuarioExtendido no existe para el usuario actual")
            es_administrador = False
        except AttributeError:
            print("Error: Método es_administrador no encontrado")
            es_administrador = False
        
        # Obtener todos los usuarios y sus perfiles
        users = User.objects.all().order_by('username')
        usuarios_info = []
        
        for user in users:
            try:
                usuario_ext = UsuarioExtendido.objects.get(user=user)
                perfiles = [p.nombre_perfil for p in usuario_ext.perfiles.all()]
                perfiles_str = ", ".join(perfiles) if perfiles else "Sin perfiles asignados"
            except UsuarioExtendido.DoesNotExist:
                print(f"Error: UsuarioExtendido no existe para el usuario {user.username}")
                perfiles_str = "Sin perfiles asignados"
            
            # Obtener la última modificación de la bitácora
            try:
                ultima_modificacion = Bitacora.objects.filter(
                    descripcion__icontains=user.username,
                    tipo_accion__in=['CREATE', 'UPDATE']
                ).order_by('-fecha_hora').first()
            except Exception as e:
                print(f"Error al obtener la última modificación para {user.username}: {str(e)}")
                ultima_modificacion = None
            
            usuarios_info.append({
                'user': user,
                'perfiles': perfiles_str,
                'can_edit': es_administrador or user == request.user,
                'ultima_modificacion': ultima_modificacion
            })
        
        # Registrar en bitácora
        try:
            registrar_evento(
                request.user,
                'VIEW',
                'USER',
                'Visualización de lista de usuarios'
            )
        except Exception as e:
            print(f"Error al registrar evento en bitácora: {str(e)}")
        
        return render(request, 'list_users.html', {
            'usuarios_info': usuarios_info,
            'es_administrador': es_administrador,
            'current_user': request.user
        })
    except Exception as e:
        print(f"Error en list_users: {str(e)}")
        return render(request, 'list_users.html', {
            'error': f'Error al cargar la lista de usuarios: {str(e)}',
            'usuarios_info': [],
            'es_administrador': False,
            'current_user': request.user
        })

@custom_login_required
def create_user(request):
    if request.method == 'GET':
        return render(request, 'create_user.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'],
                    first_name=request.POST.get('first_name', ''),
                    last_name=request.POST.get('last_name', ''),
                    email=request.POST.get('email', '')
                )
                user.save()
                
                registrar_evento(
                    request.user,
                    'CREATE',
                    'USER',
                    f'Creación de usuario: {user.username}'
                )
                
                return redirect('list_users')
            except IntegrityError:
                return render(request, 'create_user.html', {
                    'form': UserCreationForm,
                    'error': 'El nombre de usuario ya existe'
                })
        return render(request, 'create_user.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })

@custom_login_required
def edit_user(request, user_id):
    if request.method == 'POST':
        if 'password' in request.POST and request.POST['password']:
            logout(request)
            return redirect('signin')
        try:
            user = get_object_or_404(User, id=user_id)
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            
            if request.POST.get('password'):
                user.set_password(request.POST['password'])
            
            user.save()
            
            # Actualizar perfiles si es administrador
            try:
                usuario_actual = UsuarioExtendido.objects.get(user=request.user)
                if usuario_actual.es_administrador():
                    usuario_editar = UsuarioExtendido.objects.get(user=user)
                    perfiles_ids = request.POST.getlist('perfiles')
                    if perfiles_ids:
                        perfiles = Perfil.objects.filter(id_perfil__in=perfiles_ids)
                        usuario_editar.perfiles.set(perfiles)
                    else:
                        usuario_editar.perfiles.clear()
            except (UsuarioExtendido.DoesNotExist, AttributeError):
                pass
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'USER',
                f'Actualización de usuario: {user.username}'
            )
            
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('list_users')
        except Exception as e:
            messages.error(request, f'Error actualizando usuario: {str(e)}')
            return redirect('list_users')
    
    user = get_object_or_404(User, id=user_id)
    try:
        usuario_extendido = UsuarioExtendido.objects.get(user=user)
        perfiles_actuales = usuario_extendido.perfiles.all()
    except UsuarioExtendido.DoesNotExist:
        perfiles_actuales = []
    
    # Verificar si el usuario actual es administrador
    try:
        usuario_actual = UsuarioExtendido.objects.get(user=request.user)
        es_administrador = usuario_actual.es_administrador()
    except (UsuarioExtendido.DoesNotExist, AttributeError):
        es_administrador = False
    
    perfiles = Perfil.objects.all() if es_administrador else []
    
    return render(request, 'edit_user.html', {
        'user': user,
        'perfiles_actuales': perfiles_actuales,
        'perfiles': perfiles,
        'es_administrador': es_administrador
    })

@custom_login_required
def delete_user(request, user_id):
    if request.user.id == user_id:
        return render(request, 'list_users.html', {
            'users': User.objects.all(),
            'error': 'No puedes eliminar tu propio usuario'
        })
    
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    
    registrar_evento(
        request.user,
        'DELETE',
        'USER',
        f'Eliminación de usuario: {username}'
    )
    
    return redirect('list_users')

@custom_login_required
def create_perfil(request):
    if request.method == 'GET':
        return render(request, 'create_perfil.html')
    else:
        try:
            perfil = Perfil.objects.create(
                nombre_perfil=request.POST['nombre_perfil'],
                descripcion_perfil=request.POST['descripcion_perfil'],
                user_create=request.user
            )
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'CREATE',
                'PERFIL',
                f'Creación de perfil: {perfil.nombre_perfil}'
            )
            
            return redirect('list_perfiles')
        except ValueError:
            return render(request, 'create_perfil.html', {
                'error': 'Por favor proporcione datos válidos'
            })

@custom_login_required
def list_perfiles(request):
    try:
        perfiles = Perfil.objects.all()
        
        # Registrar en bitácora
        registrar_evento(
            request.user,
            'VIEW',
            'PERFIL',
            'Visualización de lista de perfiles'
        )
        
        return render(request, 'list_perfiles.html', {
            'perfiles': perfiles
        })
    except Exception as e:
        return render(request, 'list_perfiles.html', {
            'error': 'Error al cargar la lista de perfiles'
        })

@custom_login_required
def edit_perfil(request, perfil_id):
    perfil = get_object_or_404(Perfil, id_perfil=perfil_id)
    
    if request.method == 'GET':
        return render(request, 'edit_perfil.html', {
            'perfil': perfil
        })
    else:
        try:
            perfil.nombre_perfil = request.POST['nombre_perfil']
            perfil.descripcion_perfil = request.POST['descripcion_perfil']
            perfil.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'PERFIL',
                f'Actualización de perfil: {perfil.nombre_perfil}'
            )
            
            return redirect('list_perfiles')
        except ValueError:
            return render(request, 'edit_perfil.html', {
                'perfil': perfil,
                'error': 'Error actualizando el perfil'
            })

@custom_login_required
def delete_perfil(request, perfil_id):
    perfil = get_object_or_404(Perfil, id_perfil=perfil_id)
    nombre_perfil = perfil.nombre_perfil
    perfil.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'PERFIL',
        f'Eliminación de perfil: {nombre_perfil}'
    )
    
    return redirect('list_perfiles')

@custom_login_required
def create_cloud(request):
    if request.method == 'GET':
        ambientes = AMBIENTE.objects.all().order_by('nombre_ambiente')
        return render(request, 'create_cloud.html', {'ambientes': ambientes})
    try:
        # Crear el cloud
        cloud = CLOUD.objects.create(
            nombre_cloud=request.POST['nombre_cloud'],
            siglas_cloud=request.POST['siglas_cloud'],
            user_create=request.user
        )
        
        # Encontrar el ID más pequeño disponible
        ids_existentes = set(CLOUD.objects.values_list('id_cloud', flat=True))
        id_nuevo = 1
        while id_nuevo in ids_existentes:
            id_nuevo += 1
        
        cloud.id_cloud = id_nuevo
        cloud.save()
        
        # Agregar los ambientes seleccionados
        ambientes_ids = request.POST.getlist('ambientes')
        if ambientes_ids:
            ambientes = AMBIENTE.objects.filter(id_ambiente__in=ambientes_ids)
            cloud.ambientes.add(*ambientes)
        
        # Registrar en bitácora
        registrar_evento(
            request.user,
            'CREATE',
            'CLOUD',
            f'Creación de cloud: {cloud.nombre_cloud}'
        )
        
        messages.success(request, 'Cloud creado exitosamente.')
        return redirect('list_clouds')
    except Exception as e:
        ambientes = AMBIENTE.objects.all().order_by('nombre_ambiente')
        return render(request, 'create_cloud.html', {
            'ambientes': ambientes,
            'error': f'Error creando el cloud: {str(e)}'
        })

@custom_login_required
def list_clouds(request):
    try:
        clouds = CLOUD.objects.all()
        
        # Registrar en bitácora
        registrar_evento(
            request.user,
            'VIEW',
            'CLOUD',
            'Visualización de lista de clouds'
        )
        
        return render(request, 'list_clouds.html', {
            'clouds': clouds
        })
    except Exception as e:
        return render(request, 'list_clouds.html', {
            'error': 'Error al cargar la lista de clouds'
        })

@custom_login_required
def edit_cloud(request, cloud_id):
    cloud = get_object_or_404(CLOUD, id_cloud=cloud_id)
    
    if request.method == 'GET':
        ambientes = AMBIENTE.objects.all().order_by('nombre_ambiente')
        ambientes_seleccionados = cloud.ambientes.all()
        return render(request, 'edit_cloud.html', {
            'cloud': cloud,
            'ambientes': ambientes,
            'ambientes_seleccionados': ambientes_seleccionados
        })
    else:
        try:
            cloud.nombre_cloud = request.POST['nombre_cloud']
            cloud.siglas_cloud = request.POST['siglas_cloud']
            cloud.save()
            
            # Actualizar ambientes
            cloud.ambientes.clear()
            ambientes_ids = request.POST.getlist('ambientes')
            for ambiente_id in ambientes_ids:
                ambiente = get_object_or_404(AMBIENTE, id_ambiente=ambiente_id)
                cloud.ambientes.add(ambiente)
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'CLOUD',
                f'Actualización de cloud: {cloud.nombre_cloud}'
            )
            
            messages.success(request, 'Cloud actualizado exitosamente.')
            return redirect('list_clouds')
        except Exception as e:
            messages.error(request, f'Error actualizando el cloud: {str(e)}')
            ambientes = AMBIENTE.objects.all().order_by('nombre_ambiente')
            ambientes_seleccionados = cloud.ambientes.all()
            return render(request, 'edit_cloud.html', {
                'cloud': cloud,
                'ambientes': ambientes,
                'ambientes_seleccionados': ambientes_seleccionados
            })

@custom_login_required
def delete_cloud(request, cloud_id):
    cloud = get_object_or_404(CLOUD, id_cloud=cloud_id)
    nombre_cloud = cloud.nombre_cloud
    cloud.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'CLOUD',
        f'Eliminación de cloud: {nombre_cloud}'
    )
    
    return redirect('list_clouds')

@custom_login_required
def list_solicitantes(request):
    solicitantes = SOLICITANTE.objects.all().order_by('nombre_solicitante')
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'SOLICITANTE',
        'Visualización de lista de solicitantes'
    )
    
    return render(request, 'list_solicitantes.html', {'solicitantes': solicitantes})

@custom_login_required
def create_solicitante(request):
    if request.method == 'GET':
        puestos = PUESTO.objects.all().order_by('nombre_puesto')
        gerencias = GERENCIA.objects.all().order_by('nombre_gerencia')
        return render(request, 'create_solicitante.html', {
            'form': SolicitanteForm(),
            'puestos': puestos,
            'gerencias': gerencias
        })
    else:
        try:
            form = SolicitanteForm(request.POST)
            if form.is_valid():
                nuevo_solicitante = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(SOLICITANTE.objects.values_list('id_solicitante', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nuevo_solicitante.id_solicitante = id_nuevo
                nuevo_solicitante.user_create = request.user
                nuevo_solicitante.fecha_creacion = timezone.now()
                nuevo_solicitante.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'SOLICITANTE',
                    f'Creación de solicitante: {nuevo_solicitante.nombre_solicitante}'
                )
                
                return redirect('list_solicitantes')
            else:
                puestos = PUESTO.objects.all().order_by('nombre_puesto')
                gerencias = GERENCIA.objects.all().order_by('nombre_gerencia')
                return render(request, 'create_solicitante.html', {
                    'form': form,
                    'puestos': puestos,
                    'gerencias': gerencias,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            puestos = PUESTO.objects.all().order_by('nombre_puesto')
            gerencias = GERENCIA.objects.all().order_by('nombre_gerencia')
            return render(request, 'create_solicitante.html', {
                'form': SolicitanteForm(),
                'puestos': puestos,
                'gerencias': gerencias,
                'error': f'Error creando el solicitante: {str(e)}'
            })

@custom_login_required
def edit_solicitante(request, solicitante_id):
    solicitante = get_object_or_404(SOLICITANTE, id_solicitante=solicitante_id)
    
    if request.method == 'GET':
        form = SolicitanteForm(instance=solicitante)
        puestos = PUESTO.objects.all().order_by('nombre_puesto')
        gerencias = GERENCIA.objects.all().order_by('nombre_gerencia')
        return render(request, 'edit_solicitante.html', {
            'solicitante': solicitante,
            'form': form,
            'puestos': puestos,
            'gerencias': gerencias
        })
    else:
        try:
            form = SolicitanteForm(request.POST, instance=solicitante)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'SOLICITANTE',
                    f'Actualización de solicitante: {solicitante.nombre_solicitante}'
                )
                
                messages.success(request, 'Solicitante actualizado exitosamente.')
                return redirect('list_solicitantes')
            else:
                puestos = PUESTO.objects.all().order_by('nombre_puesto')
                gerencias = GERENCIA.objects.all().order_by('nombre_gerencia')
                return render(request, 'edit_solicitante.html', {
                    'solicitante': solicitante,
                    'form': form,
                    'puestos': puestos,
                    'gerencias': gerencias,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'edit_solicitante.html', {
                'solicitante': solicitante,
                'form': form,
                'error': f'Error actualizando el solicitante: {str(e)}'
            })

@custom_login_required
def delete_solicitante(request, solicitante_id):
    solicitante = get_object_or_404(SOLICITANTE, id_solicitante=solicitante_id)
    nombre_solicitante = solicitante.nombre_solicitante
    solicitante.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'SOLICITANTE',
        f'Eliminación de solicitante: {nombre_solicitante}'
    )
    
    return redirect('list_solicitantes')

@custom_login_required
def create_gerencia(request):
    if request.method == 'GET':
        return render(request, 'create_gerencia.html', {
            'form': GerenciaForm
        })
    else:
        try:
            form = GerenciaForm(request.POST)
            nueva_gerencia = form.save(commit=False)
            
            # Encontrar el ID más pequeño disponible
            ids_existentes = set(GERENCIA.objects.values_list('id_gerencia', flat=True))
            id_nuevo = 1
            while id_nuevo in ids_existentes:
                id_nuevo += 1
            
            nueva_gerencia.id_gerencia = id_nuevo
            nueva_gerencia.user_create = request.user
            nueva_gerencia.save()
            
            registrar_evento(
                request.user,
                'CREATE',
                'GERENCIA',
                f'Creación de gerencia: {nueva_gerencia.nombre_gerencia}'
            )
            
            messages.success(request, 'Gerencia creada exitosamente.')
            return redirect('submenu_crear')
        except ValueError as e:
            messages.error(request, f'Error al crear la gerencia: {str(e)}')
            return render(request, 'create_gerencia.html', {
                'form': GerenciaForm,
                'error': 'Por favor proporcione datos válidos'
            })
        except Exception as e:
            messages.error(request, f'Error inesperado al crear la gerencia: {str(e)}')
            return render(request, 'create_gerencia.html', {
                'form': GerenciaForm,
                'error': 'Error inesperado al crear la gerencia'
            })

@custom_login_required
def create_puesto(request):
    if request.method == 'GET':
        return render(request, 'create_puesto.html', {
            'form': PuestoForm
        })
    else:
        try:
            form = PuestoForm(request.POST)
            nuevo_puesto = form.save(commit=False)
            
            # Encontrar el ID más pequeño disponible
            ids_existentes = set(PUESTO.objects.values_list('id_puesto', flat=True))
            id_nuevo = 1
            while id_nuevo in ids_existentes:
                id_nuevo += 1
            
            nuevo_puesto.id_puesto = id_nuevo
            nuevo_puesto.user_create = request.user
            nuevo_puesto.save()
            
            registrar_evento(
                request.user,
                'CREATE',
                'PUESTO',
                f'Creación de puesto: {nuevo_puesto.nombre_puesto}'
            )
            
            messages.success(request, 'Puesto creado exitosamente.')
            return redirect('submenu_crear')
        except ValueError:
            messages.error(request, 'Error al crear el puesto. Por favor verifique los datos ingresados.')
            return render(request, 'create_puesto.html', {
                'form': PuestoForm(request.POST)
            })

@custom_login_required
def list_gerencias(request):
    gerencias = GERENCIA.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'GERENCIA',
        'Visualización de lista de gerencias'
    )
    
    return render(request, 'list_gerencias.html', {'gerencias': gerencias})

@custom_login_required
def list_puestos(request):
    puestos = PUESTO.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'PUESTO',
        'Visualización de lista de puestos'
    )
    
    return render(request, 'list_puestos.html', {'puestos': puestos})

@custom_login_required
def edit_gerencia(request, gerencia_id):
    gerencia = get_object_or_404(GERENCIA, id_gerencia=gerencia_id)
    
    if request.method == 'GET':
        return render(request, 'edit_gerencia.html', {'gerencia': gerencia})
    else:
        try:
            gerencia.nombre_gerencia = request.POST['nombre_gerencia']
            gerencia.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'GERENCIA',
                f'Actualización de gerencia: {gerencia.nombre_gerencia}'
            )
            
            return redirect('list_gerencias')
        except ValueError:
            return render(request, 'edit_gerencia.html', {
                'gerencia': gerencia,
                'error': 'Error actualizando la gerencia'
            })

@custom_login_required
def delete_gerencia(request, gerencia_id):
    gerencia = get_object_or_404(GERENCIA, id_gerencia=gerencia_id)
    nombre_gerencia = gerencia.nombre_gerencia
    gerencia.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'GERENCIA',
        f'Eliminación de gerencia: {nombre_gerencia}'
    )
    
    return redirect('list_gerencias')

@custom_login_required
def edit_puesto(request, puesto_id):
    puesto = get_object_or_404(PUESTO, id_puesto=puesto_id)
    
    if request.method == 'GET':
        return render(request, 'edit_puesto.html', {'puesto': puesto})
    else:
        try:
            puesto.nombre_puesto = request.POST['nombre_puesto']
            puesto.descripcion_puesto = request.POST['descripcion_puesto']
            puesto.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'PUESTO',
                f'Actualización de puesto: {puesto.nombre_puesto}'
            )
            
            return redirect('list_puestos')
        except ValueError:
            return render(request, 'edit_puesto.html', {
                'puesto': puesto,
                'error': 'Error actualizando el puesto'
            })

@custom_login_required
def delete_puesto(request, puesto_id):
    puesto = get_object_or_404(PUESTO, id_puesto=puesto_id)
    nombre_puesto = puesto.nombre_puesto
    puesto.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'PUESTO',
        f'Eliminación de puesto: {nombre_puesto}'
    )
    
    return redirect('list_puestos')

@custom_login_required
def create_vlan(request):
    if request.method == 'POST':
        form = VLANForm(request.POST)
        try:
            if form.is_valid():
                # Obtener los datos del formulario
                numero_vlan = form.cleaned_data['numero_vlan']
                cloud = form.cleaned_data['cloud']
                
                # Validar que el número de VLAN no exista en la misma cloud
                if VLAN.objects.filter(numero_vlan=numero_vlan, cloud=cloud).exists():
                    messages.error(request, f'El número de VLAN {numero_vlan} ya existe en la cloud {cloud}. Por favor, elija otro número.')
                    form.add_error('numero_vlan', f'Este número de VLAN ya existe en la cloud {cloud}.')
                    return render(request, 'create_vlan.html', {'form': form})

                vlan = form.save(commit=False)
                vlan.user_create = request.user
                
                # Validar que el segmento y barra sean válidos
                try:
                    network = ipaddress.IPv4Network(f"{vlan.segmento_vlan}/{vlan.barra_vlan}")
                except ValueError as e:
                    messages.error(request, f'El segmento de red o la barra no son válidos: {str(e)}')
                    form.add_error('segmento_vlan', f'El segmento de red o la barra no son válidos: {str(e)}')
                    return render(request, 'create_vlan.html', {'form': form})
                
                # Realizar validaciones adicionales del modelo
                try:
                    vlan.full_clean()
                except ValidationError as e:
                    for field, errors in e.message_dict.items():
                        form.add_error(field, errors[0])
                        messages.error(request, f'Error en {field}: {errors[0]}')
                    return render(request, 'create_vlan.html', {'form': form})
                
                vlan.save()

                # Crear tabla dinámica para la VLAN
                table_name = f'vlan_{vlan.numero_vlan}'
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id_vlan_ip SERIAL PRIMARY KEY,
                            ip VARCHAR(15) UNIQUE,
                            hostname VARCHAR(100),
                            usuario VARCHAR(100),
                            fecha_solicitud TIMESTAMP,
                            status VARCHAR(20) DEFAULT 'disponible'
                        )
                    """)

                # Calcular el rango de IPs disponibles
                rango_ips = f"{network[4]} - {network[-2]}"  # Desde la cuarta IP hasta una antes del broadcast

                # Crear registro en CONTROL_VLAN
                control_vlan = CONTROL_VLAN.objects.create(
                    nombre_tabla_vlan=table_name,
                    uso_red=vlan.uso_red,
                    proyecto=vlan.proyecto,
                    rango_ips_disponibles=rango_ips,
                    user_create=request.user
                )

                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'VLAN',
                    f'Creación de VLAN: {vlan.numero_vlan} - {vlan.segmento_vlan}/{vlan.barra_vlan}'
                )

                messages.success(request, 'VLAN creada exitosamente.')
                return redirect('list_vlans')
            else:
                # Si el formulario no es válido, mostrar los errores
                for field in form.errors:
                    for error in form.errors[field]:
                        messages.error(request, f'Error en {form.fields[field].label}: {error}')
                return render(request, 'create_vlan.html', {'form': form})
        except Exception as e:
            messages.error(request, f'Error al crear la VLAN: {str(e)}')
            form.add_error(None, f'Error al crear la VLAN: {str(e)}')
            return render(request, 'create_vlan.html', {'form': form})
    else:
        form = VLANForm()
    return render(request, 'create_vlan.html', {'form': form})

@custom_login_required
def list_vlans(request):
    vlans = VLAN.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'VLAN',
        'Visualización de lista de VLANs'
    )
    
    return render(request, 'list_vlans.html', {'vlans': vlans})

@custom_login_required
def edit_vlan(request, vlan_id):
    vlan = get_object_or_404(VLAN, id_vlan=vlan_id)
    
    if request.method == 'GET':
        form = VLANForm(instance=vlan)
        return render(request, 'edit_vlan.html', {
            'vlan': vlan,
            'form': form
        })
    else:
        try:
            form = VLANForm(request.POST, instance=vlan)
            if form.is_valid():
                vlan = form.save(commit=False)
                vlan.full_clean()  # Ejecutar validaciones adicionales
                vlan.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'VLAN',
                    f'Actualización de VLAN: {vlan.numero_vlan} - {vlan.segmento_vlan}/{vlan.barra_vlan}'
                )
                
                messages.success(request, 'VLAN actualizada exitosamente.')
                return redirect('list_vlans')
            else:
                return render(request, 'edit_vlan.html', {
                    'vlan': vlan,
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except ValidationError as e:
            return render(request, 'edit_vlan.html', {
                'vlan': vlan,
                'form': form,
                'error': e.messages[0]
            })
        except Exception as e:
            return render(request, 'edit_vlan.html', {
                'vlan': vlan,
                'form': form,
                'error': f'Error actualizando la VLAN: {str(e)}'
            })

@custom_login_required
def delete_vlan(request, vlan_id):
    vlan = get_object_or_404(VLAN, id_vlan=vlan_id)
    info_vlan = f"VLAN {vlan.numero_vlan} - {vlan.segmento_vlan}/{vlan.barra_vlan}"
    
    # Eliminar la tabla dinámica asociada
    table_name = f'vlan_{vlan.numero_vlan}'
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    # Eliminar el registro de CONTROL_VLAN si existe
    CONTROL_VLAN.objects.filter(nombre_tabla_vlan=table_name).delete()
    
    # Eliminar la VLAN
    vlan.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'VLAN',
        f'Eliminación de VLAN: {info_vlan}'
    )
    
    messages.success(request, 'VLAN eliminada exitosamente.')
    return redirect('list_vlans')

@custom_login_required
def get_ambientes_by_cloud(request, cloud_id):
    try:
        cloud = CLOUD.objects.get(id_cloud=cloud_id)
        ambientes = cloud.ambientes.all()
        return JsonResponse({
            'ambientes': [
                {'id': ambiente.id_ambiente, 'nombre': ambiente.nombre_ambiente}
                for ambiente in ambientes
            ]
        })
    except CLOUD.DoesNotExist:
        return JsonResponse({'error': 'Cloud no encontrada'}, status=404)

@custom_login_required
def create_proyecto(request):
    if request.method == 'GET':
        return render(request, 'create_proyecto.html', {
            'form': ProyectoForm()
        })
    else:
        try:
            form = ProyectoForm(request.POST)
            if form.is_valid():
                nuevo_proyecto = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(PROYECTO.objects.values_list('id_proyecto', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nuevo_proyecto.id_proyecto = id_nuevo
                nuevo_proyecto.user_create = request.user
                nuevo_proyecto.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'PROYECTO',
                    f'Creación de proyecto: {nuevo_proyecto.nombre_proyecto}'
                )
                
                messages.success(request, 'Proyecto creado exitosamente.')
                return redirect('list_proyectos')
            else:
                return render(request, 'create_proyecto.html', {
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'create_proyecto.html', {
                'form': ProyectoForm(),
                'error': f'Error creando el proyecto: {str(e)}'
            })

@custom_login_required
def list_proyectos(request):
    proyectos = PROYECTO.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'PROYECTO',
        'Visualización de lista de proyectos'
    )
    
    return render(request, 'list_proyectos.html', {'proyectos': proyectos})

@custom_login_required
def edit_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(PROYECTO, id_proyecto=proyecto_id)
    
    if request.method == 'GET':
        form = ProyectoForm(instance=proyecto)
        return render(request, 'edit_proyecto.html', {
            'proyecto': proyecto,
            'form': form
        })
    else:
        try:
            form = ProyectoForm(request.POST, instance=proyecto)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'PROYECTO',
                    f'Actualización de proyecto: {proyecto.nombre_proyecto}'
                )
                
                messages.success(request, 'Proyecto actualizado exitosamente.')
                return redirect('list_proyectos')
            else:
                return render(request, 'edit_proyecto.html', {
                    'proyecto': proyecto,
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'edit_proyecto.html', {
                'proyecto': proyecto,
                'form': form,
                'error': f'Error actualizando el proyecto: {str(e)}'
            })

@custom_login_required
def delete_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(PROYECTO, id_proyecto=proyecto_id)
    nombre_proyecto = proyecto.nombre_proyecto
    proyecto.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'PROYECTO',
        f'Eliminación de proyecto: {nombre_proyecto}'
    )
    
    messages.success(request, 'Proyecto eliminado exitosamente.')
    return redirect('list_proyectos')

@custom_login_required
def create_status_proyecto(request):
    if request.method == 'GET':
        return render(request, 'create_status_proyecto.html', {
            'form': StatusProyectoForm()
        })
    else:
        try:
            form = StatusProyectoForm(request.POST)
            if form.is_valid():
                nuevo_status = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(STATUS_PROYECTO.objects.values_list('id_status', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nuevo_status.id_status = id_nuevo
                nuevo_status.user_create = request.user
                nuevo_status.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'STATUS_PROYECTO',
                    f'Creación de estado de proyecto: {nuevo_status.nombre_status}'
                )
                
                messages.success(request, 'Estado de proyecto creado exitosamente.')
                return redirect('list_status_proyectos')
            else:
                return render(request, 'create_status_proyecto.html', {
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'create_status_proyecto.html', {
                'form': StatusProyectoForm(),
                'error': f'Error creando el estado de proyecto: {str(e)}'
            })

@custom_login_required
def list_status_proyectos(request):
    status_proyectos = STATUS_PROYECTO.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'STATUS_PROYECTO',
        'Visualización de lista de estados de proyecto'
    )
    
    return render(request, 'list_status_proyectos.html', {'status_proyectos': status_proyectos})

@custom_login_required
def edit_status_proyecto(request, status_id):
    status = get_object_or_404(STATUS_PROYECTO, id_status=status_id)
    
    if request.method == 'GET':
        form = StatusProyectoForm(instance=status)
        return render(request, 'edit_status_proyecto.html', {
            'status': status,
            'form': form
        })
    else:
        try:
            form = StatusProyectoForm(request.POST, instance=status)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'STATUS_PROYECTO',
                    f'Actualización de estado de proyecto: {status.nombre_status}'
                )
                
                messages.success(request, 'Estado de proyecto actualizado exitosamente.')
                return redirect('list_status_proyectos')
            else:
                return render(request, 'edit_status_proyecto.html', {
                    'status': status,
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'edit_status_proyecto.html', {
                'status': status,
                'form': form,
                'error': f'Error actualizando el estado de proyecto: {str(e)}'
            })

@custom_login_required
def delete_status_proyecto(request, status_id):
    status = get_object_or_404(STATUS_PROYECTO, id_status=status_id)
    nombre_status = status.nombre_status
    status.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'STATUS_PROYECTO',
        f'Eliminación de estado de proyecto: {nombre_status}'
    )
    
    messages.success(request, 'Estado de proyecto eliminado exitosamente.')
    return redirect('list_status_proyectos')

@custom_login_required
def create_pais(request):
    if request.method == 'GET':
        return render(request, 'create_pais.html', {
            'form': PaisForm()
        })
    else:
        try:
            form = PaisForm(request.POST)
            if form.is_valid():
                nuevo_pais = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(PAIS.objects.values_list('id_pais', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nuevo_pais.id_pais = id_nuevo
                nuevo_pais.user_create = request.user
                nuevo_pais.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'PAIS',
                    f'Creación de país: {nuevo_pais.nombre_pais}'
                )
                
                messages.success(request, 'País creado exitosamente.')
                return redirect('list_paises')
            else:
                return render(request, 'create_pais.html', {
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'create_pais.html', {
                'form': PaisForm(),
                'error': f'Error creando el país: {str(e)}'
            })

@custom_login_required
def list_paises(request):
    paises = PAIS.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'PAIS',
        'Visualización de lista de países'
    )
    
    return render(request, 'list_paises.html', {'paises': paises})

@custom_login_required
def edit_pais(request, pais_id):
    pais = get_object_or_404(PAIS, id_pais=pais_id)
    
    if request.method == 'GET':
        form = PaisForm(instance=pais)
        return render(request, 'edit_pais.html', {
            'pais': pais,
            'form': form
        })
    else:
        try:
            form = PaisForm(request.POST, instance=pais)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'PAIS',
                    f'Actualización de país: {pais.nombre_pais}'
                )
                
                messages.success(request, 'País actualizado exitosamente.')
                return redirect('list_paises')
            else:
                return render(request, 'edit_pais.html', {
                    'pais': pais,
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'edit_pais.html', {
                'pais': pais,
                'form': form,
                'error': f'Error actualizando el país: {str(e)}'
            })

@custom_login_required
def delete_pais(request, pais_id):
    pais = get_object_or_404(PAIS, id_pais=pais_id)
    nombre_pais = pais.nombre_pais
    pais.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'PAIS',
        f'Eliminación de país: {nombre_pais}'
    )
    
    messages.success(request, 'País eliminado exitosamente.')
    return redirect('list_paises')

@custom_login_required
def create_red(request):
    if request.method == 'GET':
        return render(request, 'create_red.html', {
            'form': REDForm()
        })
    else:
        try:
            form = REDForm(request.POST)
            if form.is_valid():
                nueva_red = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(RED.objects.values_list('id_red', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nueva_red.id_red = id_nuevo
                nueva_red.user_create = request.user
                nueva_red.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'RED',
                    f'Creación de red: {nueva_red.nombre_red}'
                )
                
                messages.success(request, 'Red creada exitosamente.')
                return redirect('list_redes')
            else:
                return render(request, 'create_red.html', {
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'create_red.html', {
                'form': REDForm(),
                'error': f'Error creando la red: {str(e)}'
            })

@custom_login_required
def list_redes(request):
    redes = RED.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'RED',
        'Visualización de lista de redes'
    )
    
    return render(request, 'list_redes.html', {'redes': redes})

@custom_login_required
def edit_red(request, red_id):
    red = get_object_or_404(RED, id_red=red_id)
    
    if request.method == 'GET':
        form = REDForm(instance=red)
        return render(request, 'edit_red.html', {
            'red': red,
            'form': form
        })
    else:
        try:
            form = REDForm(request.POST, instance=red)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'RED',
                    f'Actualización de red: {red.nombre_red}'
                )
                
                messages.success(request, 'Red actualizada exitosamente.')
                return redirect('list_redes')
            else:
                return render(request, 'edit_red.html', {
                    'red': red,
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'edit_red.html', {
                'red': red,
                'form': form,
                'error': f'Error actualizando la red: {str(e)}'
            })

@custom_login_required
def delete_red(request, red_id):
    red = get_object_or_404(RED, id_red=red_id)
    nombre_red = red.nombre_red
    red.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'RED',
        f'Eliminación de red: {nombre_red}'
    )
    
    messages.success(request, 'Red eliminada exitosamente.')
    return redirect('list_redes')

@custom_login_required
def create_uso_red(request):
    if request.method == 'GET':
        return render(request, 'create_uso_red.html', {
            'form': UsoRedForm()
        })
    else:
        try:
            form = UsoRedForm(request.POST)
            if form.is_valid():
                nuevo_uso = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(USO_RED.objects.values_list('id_uso_red', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nuevo_uso.id_uso_red = id_nuevo
                nuevo_uso.user_create = request.user
                nuevo_uso.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'USO_RED',
                    f'Creación de uso de red: {nuevo_uso.nombre_uso}'
                )
                
                messages.success(request, 'Uso de red creado exitosamente.')
                return redirect('list_usos_red')
            else:
                return render(request, 'create_uso_red.html', {
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'create_uso_red.html', {
                'form': UsoRedForm(),
                'error': f'Error creando el uso de red: {str(e)}'
            })

@custom_login_required
def list_usos_red(request):
    usos = USO_RED.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'USO_RED',
        'Visualización de lista de usos de red'
    )
    
    return render(request, 'list_usos_red.html', {'usos': usos})

@custom_login_required
def edit_uso_red(request, uso_id):
    uso = get_object_or_404(USO_RED, id_uso_red=uso_id)
    
    if request.method == 'GET':
        form = UsoRedForm(instance=uso)
        return render(request, 'edit_uso_red.html', {
            'uso': uso,
            'form': form
        })
    else:
        try:
            form = UsoRedForm(request.POST, instance=uso)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'USO_RED',
                    f'Actualización de uso de red: {uso.nombre_uso}'
                )
                
                messages.success(request, 'Uso de red actualizado exitosamente.')
                return redirect('list_usos_red')
            else:
                return render(request, 'edit_uso_red.html', {
                    'uso': uso,
                    'form': form,
                    'error': 'Por favor verifique los datos ingresados'
                })
        except Exception as e:
            return render(request, 'edit_uso_red.html', {
                'uso': uso,
                'form': form,
                'error': f'Error actualizando el uso de red: {str(e)}'
            })

@custom_login_required
def delete_uso_red(request, uso_id):
    uso = get_object_or_404(USO_RED, id_uso_red=uso_id)
    nombre_uso = uso.nombre_uso
    uso.delete()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'DELETE',
        'USO_RED',
        f'Eliminación de uso de red: {nombre_uso}'
    )
    
    messages.success(request, 'Uso de red eliminado exitosamente.')
    return redirect('list_usos_red')

@custom_login_required
def get_proyectos_by_uso_red(request, uso_red_id):
    try:
        uso_red = get_object_or_404(USO_RED, id_uso_red=uso_red_id)
        proyectos = PROYECTO.objects.filter(uso_red=uso_red)
        data = [{'id': p.id_proyecto, 'nombre': p.nombre_proyecto} for p in proyectos]
        return JsonResponse({'proyectos': data})
    except USO_RED.DoesNotExist:
        return JsonResponse({'error': 'Uso de red no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Error al obtener proyectos'}, status=500)

@custom_login_required
def get_redes_by_uso_red(request, uso_red_id):
    redes = RED.objects.filter(uso_red_id=uso_red_id, is_active=True)
    data = [{'id': red.id_red, 'nombre': f"{red.nombre_red} - {red.segmento_red}/{red.barra_red}"} for red in redes]
    return JsonResponse(data, safe=False)

@custom_login_required
def list_control_vlans(request):
    control_vlans = CONTROL_VLAN.objects.all()
    
    # Filtros
    nombre_tabla = request.GET.get('nombre_tabla', '')
    uso_red = request.GET.get('uso_red', '')
    proyecto = request.GET.get('proyecto', '')
    
    if nombre_tabla:
        control_vlans = control_vlans.filter(nombre_tabla_vlan__icontains=nombre_tabla)
    if uso_red:
        control_vlans = control_vlans.filter(uso_red__nombre_uso=uso_red)
    if proyecto:
        control_vlans = control_vlans.filter(proyecto__nombre_proyecto__icontains=proyecto)
    
    # Obtener listas para los selectores
    usos_red = USO_RED.objects.all()
    proyectos = PROYECTO.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'CONTROL_VLAN',
        'Visualización de lista de control de VLANs'
    )
    
    return render(request, 'list_control_vlans.html', {
        'control_vlans': control_vlans,
        'usos_red': usos_red,
        'proyectos': proyectos,
        'filtros': {
            'nombre_tabla': nombre_tabla,
            'uso_red': uso_red,
            'proyecto': proyecto
        }
    })

@custom_login_required
def create_cpu(request):
    if request.method == 'GET':
        return render(request, 'create_cpu.html', {
            'form': CPUForm()
        })
    else:
        try:
            form = CPUForm(request.POST)
            if form.is_valid():
                nueva_cpu = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(CPU.objects.values_list('cpu_id', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nueva_cpu.cpu_id = id_nuevo
                nueva_cpu.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'CPU',
                    f'Creación de CPU ID: {nueva_cpu.cpu_id} con {nueva_cpu.core_cpu} cores'
                )
                
                return redirect('list_cpus')
            else:
                return render(request, 'create_cpu.html', {
                    'form': form,
                    'error': 'Por favor proporcione datos válidos'
                })
        except ValueError:
            return render(request, 'create_cpu.html', {
                'form': CPUForm(),
                'error': 'Por favor proporcione datos válidos'
            })

@custom_login_required
def list_cpus(request):
    cpus = CPU.objects.all()
    
    # Registrar en bitácora
    registrar_evento(
        request.user,
        'VIEW',
        'CPU',
        'Visualización de lista de CPUs'
    )
    
    return render(request, 'list_cpus.html', {'list_cpus': cpus})

@custom_login_required
def edit_cpu(request, cpu_id):
    cpu = get_object_or_404(CPU, cpu_id=cpu_id)

    if request.method == 'GET':
        form = CPUForm(instance=cpu)
        return render(request, 'edit_cpu.html', {
            'form': form,
            'cpu': cpu
        })
    else:
        try:
            form = CPUForm(request.POST, instance=cpu)
            form.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'CPU',
                f'Actualización de CPU ID: {cpu.cpu_id}'
            )
            
            return redirect('list_cpus')
        except ValueError:
            return render(request, 'edit_cpu.html', {
                'form': form,
                'cpu': cpu,
                'error': 'Error actualizando la CPU'
            })

@custom_login_required
def delete_cpu(request, cpu_id):
    cpu = get_object_or_404(CPU, cpu_id=cpu_id)
    if request.method == 'POST':
        # Registrar en bitácora
        registrar_evento(
            request.user,
            'DELETE',
            'CPU',
            f'Eliminación de CPU ID: {cpu.cpu_id}'
        )
        cpu.delete()
        return redirect('list_cpus')

@custom_login_required
def create_vti(request):
    if request.method == 'GET':
        return render(request, 'create_vti.html', {
            'form': VTIForm()
        })
    else:
        try:
            form = VTIForm(request.POST)
            if form.is_valid():
                nueva_vti = form.save(commit=False)
                
                # Encontrar el ID más pequeño disponible
                ids_existentes = set(VTI.objects.values_list('vti_id', flat=True))
                id_nuevo = 1
                while id_nuevo in ids_existentes:
                    id_nuevo += 1
                
                nueva_vti.vti_id = id_nuevo
                nueva_vti.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'CREATE',
                    'VTI',
                    f'Creación de VTI ID: {nueva_vti.vti_id} - {nueva_vti.nombre_vti}'
                )
                
                return redirect('list_vtis')
            else:
                return render(request, 'create_vti.html', {
                    'form': form,
                    'error': 'Por favor proporcione datos válidos'
                })
        except ValueError:
            return render(request, 'create_vti.html', {
                'form': VTIForm(),
                'error': 'Por favor proporcione datos válidos'
            })

@custom_login_required
def list_vtis(request):
    vtis = VTI.objects.all().order_by('vti_id')
    return render(request, 'list_vtis.html', {
        'vtis': vtis
    })

@custom_login_required
def edit_vti(request, vti_id):
    vti = get_object_or_404(VTI, vti_id=vti_id)
    if request.method == 'GET':
        form = VTIForm(instance=vti)
        return render(request, 'edit_vti.html', {
            'vti': vti,
            'form': form
        })
    else:
        try:
            form = VTIForm(request.POST, instance=vti)
            if form.is_valid():
                form.save()
                
                # Registrar en bitácora
                registrar_evento(
                    request.user,
                    'UPDATE',
                    'VTI',
                    f'Actualización de VTI ID: {vti.vti_id} - {vti.nombre_vti}'
                )
                
                return redirect('list_vtis')
            else:
                return render(request, 'edit_vti.html', {
                    'vti': vti,
                    'form': form,
                    'error': 'Por favor proporcione datos válidos'
                })
        except ValueError:
            return render(request, 'edit_vti.html', {
                'vti': vti,
                'form': VTIForm(instance=vti),
                'error': 'Por favor proporcione datos válidos'
            })

@custom_login_required
def delete_vti(request, vti_id):
    vti = get_object_or_404(VTI, vti_id=vti_id)
    if request.method == 'POST':
        # Registrar en bitácora antes de eliminar
        registrar_evento(
            request.user,
            'DELETE',
            'VTI',
            f'Eliminación de VTI ID: {vti.vti_id} - {vti.nombre_vti}'
        )
        vti.delete()
        return redirect('list_vtis')
    return render(request, 'delete_vti.html', {
        'vti': vti
    })
