from django.contrib import admin
from django.utils.html import format_html
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'price', 'image_tag')  
    search_fields = ('title',)

    def image_tag(self, obj):
        if obj.image:  # Check if an image exists
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;"/>', obj.image.url)
        return "No Image"
    
    image_tag.short_description = 'Image'

admin.site.register(Post, PostAdmin)

