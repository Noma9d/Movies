from django.contrib import admin
from .models import  Picture, ScreeList, TorrentFile, Tag, Actor, Record
# Register your models here.


admin.site.register(Picture)
admin.site.register(ScreeList)
admin.site.register(TorrentFile)
admin.site.register(Tag)
admin.site.register(Actor)
admin.site.register(Record)