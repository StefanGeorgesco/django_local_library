from django.test import TestCase

# Create your tests here.

from catalog.models import Genre, Language, Book, BookInstance, Author
from django.utils.translation import ugettext_lazy as _
import datetime

class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # Create a genre
        Genre.objects.create(name='Fantasy')

    def test_name_label(self):
        genre=Genre.objects.get(id=1)
        field_label=genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, _('genre'))

    def test_name_help_text(self):
        genre=Genre.objects.get(id=1)
        help_text=genre._meta.get_field('name').help_text
        self.assertEqual(help_text, _('Enter a book genre (e.g. Science Fiction)'))

    def test_string_representation(self):
        genre=Genre.objects.get(id=1)
        self.assertEqual(str(genre), 'Fantasy')

class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # Create a language
        Language.objects.create(name='Chinese')

    def test_name_label(self):
        language=Language.objects.get(id=1)
        field_label=language._meta.get_field('name').verbose_name
        self.assertEqual(field_label, _('language'))

    def test_name_help_text(self):
        language=Language.objects.get(id=1)
        help_text=language._meta.get_field('name').help_text
        self.assertEqual(help_text, _('Enter a language (e.g. English)'))

    def test_string_representation(self):
        language=Language.objects.get(id=1)
        self.assertEqual(str(language), 'Chinese')

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        # Create a book
        Genre.objects.create(name='Fantasy')
        Genre.objects.create(name='Poems')
        test_language=Language.objects.create(name='French')
        test_author=Author.objects.create(first_name='Antoine', last_name='de Saint Exupéry')
        test_book=Book.objects.create(
            title='Le petit prince',
            author=test_author,
            summary='a beautiful book',
            isbn='123-567890123',
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

    def test_title_label(self):
        book=Book.objects.get(id=1)
        field_label=book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, _('title'))

    def test_author_label(self):
        book=Book.objects.get(id=1)
        field_label=book._meta.get_field('author').verbose_name
        self.assertEqual(field_label, _('author'))

    def test_summary_label(self):
        book=Book.objects.get(id=1)
        field_label=book._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, _('summary'))

    def test_summary_help_text(self):
        book=Book.objects.get(id=1)
        help_text=book._meta.get_field('summary').help_text
        self.assertEqual(help_text, _('Enter a brief description of the book'))

    def test_isbn_label(self):
        book=Book.objects.get(id=1)
        field_label=book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label, 'ISBN')

    def test_isbn_help_text(self):
        book=Book.objects.get(id=1)
        help_text=book._meta.get_field('isbn').help_text
        self.assertEqual(help_text, _('13 Character ')+'<a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    def test_genre_label(self):
        book=Book.objects.get(id=1)
        field_label=book._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, _('genre'))

    def test_genre_help_text(self):
        book=Book.objects.get(id=1)
        help_text=book._meta.get_field('genre').help_text
        self.assertEqual(help_text, _('Select one or several genre(s) for this book'))

    def test_language_label(self):
        book=Book.objects.get(id=1)
        field_label=book._meta.get_field('language').verbose_name
        self.assertEqual(field_label, _('language'))

    def test_language_help_text(self):
        book=Book.objects.get(id=1)
        help_text=book._meta.get_field('language').help_text
        self.assertEqual(help_text, _('Select the language of the original version of this book'))

    def test_string_representation(self):
        book=Book.objects.get(id=1)
        self.assertEqual(str(book), 'Le petit prince')

    def test_display_genre(self):
        book=Book.objects.get(id=1)
        self.assertEqual(book.display_genre(), 'Fantasy, Poems')
        self.assertEqual(book.display_genre.short_description, _('Genre'))

    def test_get_absolute_url(self):
        book=Book.objects.get(id=1)
        self.assertEqual(book.get_absolute_url(), '/catalog/book/1')

class BookInstanceTest(TestCase):
    def setUp(self):
        # Set up non-modified objects used by all test methods
        # Create a book
        Genre.objects.create(name='Fantasy')
        Genre.objects.create(name='Poems')
        test_language=Language.objects.create(name='French')
        test_author=Author.objects.create(first_name='Antoine', last_name='de Saint Exupéry')
        test_book=Book.objects.create(
            title='Le petit prince',
            author=test_author,
            summary='a beautiful book',
            isbn='123-567890123',
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a book instance
        return_date = datetime.date.today() - datetime.timedelta(days=1)
        status = 'm'
        self.book_instance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            status=status,
        )

        # Create a second book instance, without book
        return_date = datetime.date.today() - datetime.timedelta(days=1)
        status = 'm'
        self.book_instance2 = BookInstance.objects.create(
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            status=status,
        )

    def test_id_help_text(self):
        help_text = self.book_instance1._meta.get_field('id').help_text
        self.assertEqual(help_text, _('Unique ID for this particular book across whole library'))

    def test_language_help_text(self):
        help_text = self.book_instance1._meta.get_field('language').help_text
        self.assertEqual(help_text, _('Select the language of this copy of the book'))

    def test_imprint_label(self):
        field_label = self.book_instance1._meta.get_field('imprint').verbose_name
        self.assertEqual(field_label, _('imprint'))

    def test_due_back_label(self):
        field_label = self.book_instance1._meta.get_field('due_back').verbose_name
        self.assertEqual(field_label, _('due back'))

    def test_status_label(self):
        field_label = self.book_instance1._meta.get_field('status').verbose_name
        self.assertEqual(field_label, _('status'))

    def test_status_help_text(self):
        help_text =self.book_instance1._meta.get_field('status').help_text
        self.assertEqual(help_text, _('Book availability'))

    def test_string_representation(self):
        self.assertEqual(str(self.book_instance1), f'{self.book_instance1.id} (Le petit prince)')
        self.assertEqual(str(self.book_instance2), f'{self.book_instance2.id} (no book)')

    def test_display_title(self):
        self.assertEqual(self.book_instance1.display_title(), 'Le petit prince')
        self.assertEqual(self.book_instance1.display_title.short_description, 'Title')
        self.assertEqual(self.book_instance2.display_title(), 'no book')
        self.assertEqual(self.book_instance2.display_title.short_description, 'Title')

    def test_is_overdue_property(self):
        self.assertTrue(self.book_instance1.is_overdue)

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, _('first name'))

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, _('last name'))

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, _('birth date'))

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, _('died'))

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 100)

    def test_string_representation(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}' # 'Bob, Big'
        self.assertEqual(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')
