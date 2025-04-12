from django.contrib import admin
from .models import Genre, Book, BookInstance, Author,Language

# Register your models here.
class BookInline(admin.TabularInline):
    model=Book
    extra=2

class AuthorAdmin(admin.ModelAdmin):
    list_display=('first_name','last_name','date_of_birth','date_of_death')
    fields=['first_name','last_name',('date_of_birth','date_of_death')]
    inlines=[BookInline]
    
class BooksInstanceInline(admin.TabularInline):
    model=BookInstance
    extra=2

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines=[BooksInstanceInline]

class BookInstanceAdmin(admin.ModelAdmin):
    list_display=('book','status','due_back')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back',"borrower")
        }),
    )


# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)

admin.site.register(Author,AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookInstance,BookInstanceAdmin)
