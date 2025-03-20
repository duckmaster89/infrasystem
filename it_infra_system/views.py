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
        # Obtener el perfil del usuario actual
        usuario_extendido = UsuarioExtendido.objects.get(user=request.user)
        es_administrador = usuario_extendido.perfil.nombre_perfil == 'Administrador'
        
        # Obtener todos los usuarios y sus perfiles
        users = User.objects.all().order_by('username')
        usuarios_info = []
        for user in users:
            try:
                perfil = UsuarioExtendido.objects.get(user=user).perfil.nombre_perfil
            except UsuarioExtendido.DoesNotExist:
                perfil = "Sin perfil asignado"
            usuarios_info.append({
                'user': user,
                'perfil': perfil,
                'can_edit': es_administrador or user == request.user
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
    user = get_object_or_404(User, id=user_id)
    
    # Verificar si el usuario tiene permiso para editar
    try:
        usuario_extendido = UsuarioExtendido.objects.get(user=request.user)
        es_administrador = usuario_extendido.perfil.nombre_perfil == 'Administrador'
        if not (es_administrador or request.user.id == user_id):
            return redirect('list_users')
    except UsuarioExtendido.DoesNotExist:
        return redirect('list_users')
    
    if request.method == 'GET':
        try:
            perfil = UsuarioExtendido.objects.get(user=user).perfil
        except UsuarioExtendido.DoesNotExist:
            perfil = None
            
        return render(request, 'edit_user.html', {
            'user': user,
            'perfil': perfil
        })
    else:
        try:
            # Actualizar datos básicos del usuario
            user.username = request.POST['username']
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            
            # Actualizar contraseña si se proporcionó
            if request.POST.get('password1') and request.POST['password1'] == request.POST['password2']:
                user.set_password(request.POST['password1'])
            
            user.save()
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'UPDATE',
                'USER',
                f'Actualización de usuario: {user.username}'
            )
            
            # Si el usuario editó su propia contraseña, necesita volver a iniciar sesión
            if request.POST.get('password1') and request.user.id == user_id:
    logout(request)
                return redirect('signin')
            
            return redirect('list_users')
        except ValueError as e:
            return render(request, 'edit_user.html', {
                'user': user,
                'error': f'Error actualizando el usuario: {str(e)}'
            })
        except Exception as e:
            return render(request, 'edit_user.html', {
                'user': user,
                'error': 'Error inesperado actualizando el usuario'
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
        return render(request, 'create_cloud.html', {
            'ambientes': ambientes
            })
        else:
        try:
            # Crear el cloud
            cloud = CLOUD.objects.create(
                nombre_cloud=request.POST['nombre_cloud'],
                siglas_cloud=request.POST['siglas_cloud'],
                user_create=request.user
            )
            
            # Agregar los ambientes seleccionados
            ambientes_ids = request.POST.getlist('ambientes')
            for ambiente_id in ambientes_ids:
                ambiente = get_object_or_404(AMBIENTE, id_ambiente=ambiente_id)
                cloud.ambientes.add(ambiente)
            
            # Registrar en bitácora
            registrar_evento(
                request.user,
                'CREATE',
                'CLOUD',
                f'Creación de cloud: {cloud.nombre_cloud}'
            )
            
            return redirect('list_clouds')
        except ValueError:
            ambientes = AMBIENTE.objects.all().order_by('nombre_ambiente')
            return render(request, 'create_cloud.html', {
                'ambientes': ambientes,
                'error': 'Por favor proporcione datos válidos'
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
def create_solicitante(request):
    if request.method == 'GET':
        return render(request, 'create_solicitante.html', {
            'form': SolicitanteForm
        })
    else:
        try:
            form = SolicitanteForm(request.POST)
            nuevo_solicitante = form.save(commit=False)
            nuevo_solicitante.user_create = request.user
            nuevo_solicitante.save()
            
            registrar_evento(
                request.user,
                'CREATE',
                'SOLICITANTE',
                f'Creación de solicitante: {nuevo_solicitante.nombre_solicitante}'
            )
            
            messages.success(request, 'Solicitante creado exitosamente.')
            return redirect('submenu_crear')
        except ValueError:
            return render(request, 'create_solicitante.html', {
                'form': SolicitanteForm,
                'error': 'Por favor proporcione datos válidos'
            })

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
def list_solicitantes(request):
    try:
        solicitantes = SOLICITANTE.objects.all()
        return render(request, 'list_solicitantes.html', {'solicitantes': solicitantes})
    except Exception as e:
        return render(request, 'list_solicitantes.html', {'error': str(e)})

@custom_login_required
def list_gerencias(request):
    try:
        gerencias = GERENCIA.objects.all()
        return render(request, 'list_gerencias.html', {'gerencias': gerencias})
    except Exception as e:
        return render(request, 'list_gerencias.html', {'error': str(e)})

@custom_login_required
def list_puestos(request):
    try:
        puestos = PUESTO.objects.all()
        return render(request, 'list_puestos.html', {'puestos': puestos})
    except Exception as e:
        return render(request, 'list_puestos.html', {'error': str(e)})

@custom_login_required
def edit_solicitante(request, solicitante_id):
    solicitante = get_object_or_404(SOLICITANTE, id_solicitante=solicitante_id)
    
    if request.method == 'GET':
        return render(request, 'edit_solicitante.html', {
            'form': SolicitanteForm(instance=solicitante)
        })
    else:
        try:
            form = SolicitanteForm(request.POST, instance=solicitante)
            form.save()
            
            registrar_evento(
                request.user,
                'UPDATE',
                'SOLICITANTE',
                f'Actualización de solicitante: {solicitante.nombre_solicitante}'
            )
            
            messages.success(request, 'Solicitante actualizado exitosamente.')
            return redirect('list_solicitantes')
        except ValueError:
            return render(request, 'edit_solicitante.html', {
                'form': SolicitanteForm(instance=solicitante),
                'error': 'Error actualizando el solicitante'
            })

@custom_login_required
def delete_solicitante(request, solicitante_id):
    solicitante = get_object_or_404(SOLICITANTE, id_solicitante=solicitante_id)
    nombre_solicitante = solicitante.nombre_solicitante
    solicitante.delete()
    
    registrar_evento(
        request.user,
        'DELETE',
        'SOLICITANTE',
        f'Eliminación de solicitante: {nombre_solicitante}'
    )
    
    messages.success(request, 'Solicitante eliminado exitosamente.')
    return redirect('list_solicitantes')

@custom_login_required
def edit_gerencia(request, gerencia_id):
    gerencia = get_object_or_404(GERENCIA, id_gerencia=gerencia_id)
    
    if request.method == 'GET':
        return render(request, 'edit_gerencia.html', {
            'form': GerenciaForm(instance=gerencia)
        })
    else:
        try:
            form = GerenciaForm(request.POST, instance=gerencia)
            form.save()
            
            registrar_evento(
                request.user,
                'UPDATE',
                'GERENCIA',
                f'Actualización de gerencia: {gerencia.nombre_gerencia}'
            )
            
            messages.success(request, 'Gerencia actualizada exitosamente.')
            return redirect('list_gerencias')
        except ValueError:
            return render(request, 'edit_gerencia.html', {
                'form': GerenciaForm(instance=gerencia),
                'error': 'Error actualizando la gerencia'
            })

@custom_login_required
def delete_gerencia(request, gerencia_id):
    gerencia = get_object_or_404(GERENCIA, id_gerencia=gerencia_id)
    nombre_gerencia = gerencia.nombre_gerencia
    gerencia.delete()
    
    registrar_evento(
        request.user,
        'DELETE',
        'GERENCIA',
        f'Eliminación de gerencia: {nombre_gerencia}'
    )
    
    messages.success(request, 'Gerencia eliminada exitosamente.')
    return redirect('list_gerencias')

@custom_login_required
def edit_puesto(request, puesto_id):
    puesto = get_object_or_404(PUESTO, id_puesto=puesto_id)
    
    if request.method == 'GET':
        return render(request, 'edit_puesto.html', {
            'form': PuestoForm(instance=puesto)
        })
    else:
        try:
            form = PuestoForm(request.POST, instance=puesto)
            form.save()
            
            registrar_evento(
                request.user,
                'UPDATE',
                'PUESTO',
                f'Actualización de puesto: {puesto.nombre_puesto}'
            )
            
            messages.success(request, 'Puesto actualizado exitosamente.')
            return redirect('list_puestos')
        except ValueError:
            return render(request, 'edit_puesto.html', {
                'form': PuestoForm(instance=puesto),
                'error': 'Error actualizando el puesto'
            })

@custom_login_required
def delete_puesto(request, puesto_id):
    puesto = get_object_or_404(PUESTO, id_puesto=puesto_id)
    nombre_puesto = puesto.nombre_puesto
    puesto.delete()
    
    registrar_evento(
        request.user,
        'DELETE',
        'PUESTO',
        f'Eliminación de puesto: {nombre_puesto}'
    )
    
    messages.success(request, 'Puesto eliminado exitosamente.')
    return redirect('list_puestos')
