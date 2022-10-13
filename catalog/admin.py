from django.contrib import admin
from .models import Genre, Language, Book, Author, BookInstance

# Register your models here.

admin.site.register(Genre)

admin.site.register(Language)

class BooksInline(admin.TabularInline):
    model = Book
    extra = 0


class AuthhorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] 
    
    inlines = [BooksInline]
admin.site.register(Author, AuthhorAdmin)

class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    
    inlines = [BookInstanceInline]

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'imprint', 'status', 'borrower', 'due_back')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields' : ('status', 'borrower', 'due_back')
        }),
    )