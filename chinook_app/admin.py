from django.contrib import admin
from .models import Artist, Album, Track

# Register your models here.

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artistid')

admin.site.register(Artist)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Track)