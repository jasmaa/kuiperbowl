from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Question)
admin.site.register(User)
admin.site.register(Player)
admin.site.register(Room)
admin.site.register(Message)
