from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .forms import AmbienteForm, SolicitanteForm, GerenciaForm, PuestoForm
from .models import AMBIENTE, Bitacora, Perfil, UsuarioExtendido, CLOUD, SOLICITANTE, GERENCIA, PUESTO
from django.contrib import messages
from .decorators import custom_login_required


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

            # Crear usuario extendido sin perfil
            UsuarioExtendido.objects.create(user=user)

            messages.success(request, 'Usuario creado exitosamente. Por favor, espere a que un administrador le asigne un perfil.')
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
            # Verificar si el usuario tiene un perfil asignado
            try:
                usuario_extendido = UsuarioExtendido.objects.get(user=user)
                if not usuario_extendido.perfil:
                    messages.error(request, 'No tiene un perfil asignado. Por favor, contacte al administrador.')
                    return render(request, 'signin.html', {'error': 'No tiene un perfil asignado'})
                
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
            es_administrador = usuario_extendido.perfil.nombre_perfil == 'Administrador'
        except (UsuarioExtendido.DoesNotExist, AttributeError):
            es_administrador = False
        
        # Obtener todos los usuarios y sus perfiles
        users = User.objects.all().order_by('username')
        usuarios_info = []
        
        for user in users:
            try:
                usuario_ext = UsuarioExtendido.objects.get(user=user)
                perfil = usuario_ext.perfil.nombre_perfil if usuario_ext.perfil else "Sin perfil asignado"
            except UsuarioExtendido.DoesNotExist:
                perfil = "Sin perfil asignado"
            
            # Obtener la última modificación de la bitácora
            ultima_modificacion = Bitacora.objects.filter(
                descripcion__icontains=user.username,
                tipo_accion__in=['CREATE', 'UPDATE']
            ).order_by('-fecha_hora').first()
            
            usuarios_info.append({
                'user': user,
                'perfil': perfil,
                'can_edit': es_administrador or user == request.user,
                'ultima_modificacion': ultima_modificacion
            })
        
        # Registrar en bitácora
        registrar_evento(
            request.user,
            'VIEW',
            'USER',
            'Visualización de lista de usuarios'
        )
        
        return render(request, 'list_users.html', {
            'usuarios_info': usuarios_info,
            'es_administrador': es_administrador,
            'current_user': request.user
        })
    except Exception as e:
        print(f"Error en list_users: {str(e)}")
        return render(request, 'list_users.html', {
            'error': 'Error al cargar la lista de usuarios'
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
            
            # Actualizar perfil si es administrador
            try:
                usuario_actual = UsuarioExtendido.objects.get(user=request.user)
                if usuario_actual.perfil.nombre_perfil == 'Administrador':
                    usuario_editar = UsuarioExtendido.objects.get(user=user)
                    perfil_id = request.POST.get('perfil')
                    if perfil_id:
                        perfil = get_object_or_404(Perfil, id=perfil_id)
                        usuario_editar.perfil = perfil
                        usuario_editar.save()
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
        perfil_actual = usuario_extendido.perfil
    except UsuarioExtendido.DoesNotExist:
        perfil_actual = None
    
    # Verificar si el usuario actual es administrador
    try:
        usuario_actual = UsuarioExtendido.objects.get(user=request.user)
        es_administrador = usuario_actual.perfil.nombre_perfil == 'Administrador'
    except (UsuarioExtendido.DoesNotExist, AttributeError):
        es_administrador = False
    
    perfiles = Perfil.objects.all() if es_administrador else []
    
    return render(request, 'edit_user.html', {
        'user': user,
        'perfil_actual': perfil_actual,
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
            
            return redirect('list_clouds')
        except ValueError:
            ambientes = AMBIENTE.objects.all().order_by('nombre_ambiente')
            return render(request, 'edit_cloud.html', {
                'cloud': cloud,
                'ambientes': ambientes,
                'error': 'Error actualizando el cloud'
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
