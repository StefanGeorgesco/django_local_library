from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
import uuid # Required for unique book instances
from datetime import date
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(_('genre'), max_length=200, help_text=_('Enter a book genre (e.g. Science Fiction)'))

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Language(models.Model):
    """Model representing a language used in the original version of the book and in a book instance."""
    name = models.CharField(_('language'), max_length=40, help_text=_('Enter a language (e.g. English)'))

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(_('title'), max_length=200)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(_('summary'), max_length=1000, help_text=_('Enter a brief description of the book'))
    isbn = models.CharField('ISBN', max_length=13, help_text=_('13 Character ')+'<a href="https://www.isbn-international.org/content/what-isbn" target="_blank">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text=_('Select one or several genre(s) for this book'))
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, help_text=_('Select the language of the original version of this book'))

    class Meta:
        permissions = (("can_edit_book", "Can edit book data"),)
        ordering = ['title']

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = _('Genre')

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=_('Unique ID for this particular book across whole library'))
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, help_text=_('Select the language of this copy of the book'))
    imprint = models.CharField(_('imprint'), max_length=200)
    due_back = models.DateField(_('due back'), null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        _('status'),
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text=_('Book availability'),
    )

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        if self.book:
            title = self.book.title
        else:
            title = 'no book'
        return f'{self.id} ({title})'

    def display_title(self):
        """Create a string for the book title. This is required to display title in Admin."""
        if self.book:
            title = self.book.title
        else:
            title = 'no book'
        return title

    display_title.short_description = 'Title'

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    date_of_birth = models.DateField(_('birth date'), null=True, blank=True)
    date_of_death = models.DateField(_('died'), null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        permissions = (("can_edit_author", "Can edit author data"),)

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
