from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Track, Album, Artist, Mediatype
import random

# Create your views here.

def listado(request):
    if request.method == 'POST':
        artista_nombre = request.POST['artista']
        album_nombre = request.POST['album']
        cancion_nombre = request.POST['cancion']
        compositor_nombre = request.POST['compositor']
        
        # Obtener o crear el objeto del artista
        try:
            artista = Artist.objects.get(name=artista_nombre) # Para no duplicar el nombre del artista
        except Artist.DoesNotExist:
            ultimo_artistid = Artist.objects.aggregate(Max('artistid'))['artistid__max']
            nuevo_artistid = ultimo_artistid + 1 if ultimo_artistid is not None else 1
            artista, _ = Artist.objects.get_or_create(artistid=nuevo_artistid, name=artista_nombre)
        
        # Obtener o crear el objeto del álbum
        try:
            album = Album.objects.get(title=album_nombre, artistid=artista)
        except Album.DoesNotExist:
            ultimo_albumid = Album.objects.aggregate(Max('albumid'))['albumid__max']
            nuevo_albumid = ultimo_albumid + 1 if ultimo_albumid is not None else 1
            album, _ = Album.objects.get_or_create(albumid=nuevo_albumid, title=album_nombre, artistid=artista)
        
        # Obtener un valor aleatorio de mediatypeid entre 1 y 5
        mediatype_random_id = random.randint(1, 5)
        mediatype_default = Mediatype.objects.get(mediatypeid=mediatype_random_id)
        
        # Obtener el último valor de trackid en la base de datos
        ultimo_trackid = Track.objects.aggregate(Max('trackid'))['trackid__max']
        
        # Generar un nuevo ID sumando 1 al último valor
        nuevo_trackid = ultimo_trackid + 1 if ultimo_trackid is not None else 1
        
        # Crear el objeto Track con el nuevo ID y los demás valores
        track = Track.objects.create(
            trackid=nuevo_trackid, 
            name=cancion_nombre, 
            albumid=album, 
            composer=compositor_nombre, 
            mediatypeid=mediatype_default)
        
        return redirect('/listado/')
    
    else:    
        artista_seleccionado = request.GET.get('artist')    
        tracks = Track.objects.all().order_by('albumid__artistid__name')
        
        if artista_seleccionado:
            tracks = tracks.filter(albumid__artistid__name=artista_seleccionado)
        
        # Obtener los nombres únicos de los artistas usando un conjunto (set)
        artistas = set(track.albumid.artistid.name for track in tracks)

        # Convertir el conjunto de artistas en una lista y ordenarla alfabéticamente
        artistas_ordenados = sorted(list(artistas))
        
        # Obtener el valor del parámetro de cantidad de entradas por página de la URL
        paginate_by = request.GET.get('paginate_by', 10)

        paginator = Paginator(tracks, paginate_by)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)

        return render(request, 'listado.html', {'page': page, 'artistas': artistas_ordenados, 'artista_seleccionado': artista_seleccionado})
    
def editar(request, id):
    track = Track.objects.get(trackid=id)
    
    return render(request, 'editar.html', {'track':track})

def editar_track(request):
    track_id = request.POST['trackid']
    artista_nombre = request.POST['artista']
    album_nombre = request.POST['album']
    cancion_nombre = request.POST['cancion']
    compositor_nombre = request.POST['compositor']

    try:
        track = Track.objects.get(trackid=track_id)

        # Buscar el objeto del artista por su artistid en lugar de su nombre
        artista = Artist.objects.get(artistid=track.albumid.artistid.artistid)
    except (Track.DoesNotExist, Artist.DoesNotExist):
        track = None
        artista = None

    if track and artista:
        track.name = cancion_nombre
        track.composer = compositor_nombre

        # Actualizar el nombre del artista y guardar el cambio
        artista.name = artista_nombre
        artista.save()

        if album_nombre.strip():
            track.albumid.title = album_nombre
            track.albumid.save()

        track.save()

    return redirect('/listado/')

def agregar(request):
    return render(request, 'agregar.html')

def index(request):
    mostrar_boton_agregar = False
    return render(request, 'index.html', {'mostrar_boton_agregar': mostrar_boton_agregar})

def eliminar(request, id):
    if request.method == 'GET':
        # Obtener el objeto Track con el trackid específico o mostrar una página 404 si no existe
        track = get_object_or_404(Track, trackid=id)

        # Eliminar el objeto Track de la base de datos
        track.delete()

        # Redirigir al listado de tracks después de eliminar
        return redirect('/listado/')