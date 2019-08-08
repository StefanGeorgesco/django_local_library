from django.contrib import admin

# Register your models here.
from catalog.models import Genre, Language, Book, BookInstance, Author

admin.site.register(Genre)
admin.site.register(Language)
#admin.site.register(Book) #standard registration
#admin.site.register(BookInstance) #standard registration
#admin.site.register(Author) #standard registration

class BooksInline(admin.StackedInline):
    model = Book
    extra = 0

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]

# Register the Admin classes for Book the classical way, after class definition
admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Register the Admin classes for Book using the decorator, before class definition
@admin.register(Book)
# Define the admin class
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre', 'language')
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator, before class definition
@admin.register(BookInstance)
# Define the admin class
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('display_title', 'language', 'imprint', 'status', 'due_back', 'borrower', 'id')
    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id', 'language')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
