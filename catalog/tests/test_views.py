from django.test import TestCase

# Create your tests here.

from django.urls import reverse
import datetime, uuid
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User # Required to assign User as a borrower
from django.contrib.auth.models import Permission # Required to grant the permission needed to set a book as returned.
from catalog.models import Author, Book, BookInstance, Genre, Language

class indexTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 4 genres :
        number_of_genres = 4
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create 3 languages :
        Language.objects.create(name='English')
        Language.objects.create(name='French')
        Language.objects.create(name='German')
        # Create 2 authors :
        test_author1 = Author.objects.create(first_name='John', last_name='Smith')
        test_author2 = Author.objects.create(first_name='Paul', last_name='Mc Cartney')
        # Create 5 books
        number_of_books = 5
        for book_id in range(number_of_books):
            test_book = Book.objects.create(
                title=f'Book Title {book_id}',
                summary=f'My book summary {book_id}',
                isbn='ABCDEFG',
                author=test_author1 if book_id % 2 else test_author2,
                language=Language.objects.all()[book_id % 3],
            )
            test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
            test_book.save()
        # Create 30 book instances (copies) :
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = datetime.date.today() + datetime.timedelta(days=book_copy%5)
            status = ['m', 'o', 'a', 'r'][book_copy % 4]
            BookInstance.objects.create(
                book=Book.objects.all()[book_copy % 5],
                imprint=f'Unlikely Imprint, 2016 #{book_copy}',
                due_back=return_date,
                status=status,
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_context_data(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['num_books'], 5)
        self.assertEqual(response.context['num_instances'], 30)
        self.assertEqual(response.context['num_instances_available'], 7)
        self.assertEqual(response.context['num_instances_reserved'], 7)
        self.assertEqual(response.context['num_instances_loan'], 8)
        self.assertEqual(response.context['num_instances_maintenance'], 8)
        self.assertEqual(response.context['num_authors'], 2)
        self.assertEqual(response.context['num_genres'], 4)
        self.assertEqual(response.context['num_languages'], 3)
        self.assertEqual(response.context['num_visits'], 1)

class BookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 4 genres :
        number_of_genres = 4
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create 3 languages :
        Language.objects.create(name='English')
        Language.objects.create(name='French')
        Language.objects.create(name='German')
        # Create 2 authors :
        test_author1 = Author.objects.create(first_name='John', last_name='Smith')
        test_author2 = Author.objects.create(first_name='Paul', last_name='Mc Cartney')
        # Create 12 books
        number_of_books = 12
        for book_id in range(number_of_books):
            test_book = Book.objects.create(
                title=f'Book Title {book_id}',
                summary=f'My book summary {book_id}',
                isbn='ABCDEFG',
                author=test_author1 if book_id % 2 else test_author2,
                language=Language.objects.all()[book_id % 3],
            )
            test_book.genre.set(genre_objects_for_book[:book_id % 4]) # Direct assignment of many-to-many types not allowed.
            test_book.save()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/books/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['book_list']), 10)

    def test_lists_all_books(self):
        # Get second page and confirm it has (exactly) 2 remaining items
        response = self.client.get(reverse('books')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['book_list']), 2)

class BookDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create a language :
        test_language = Language.objects.create(name='English')
        # Create an author :
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        # Create a book
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()
        # Create 4 book instances (copies) of that book
        number_of_book_copies = 4
        for book_copy in range(number_of_book_copies):
            return_date = datetime.date.today() + datetime.timedelta(days=book_copy+1)
            status = ['m', 'o', 'a', 'r'][book_copy]
            BookInstance.objects.create(
                book=test_book,
                imprint=f'Unlikely Imprint, 2016 #{book_copy}',
                due_back=return_date,
                status=status,
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/book/1')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('book-detail', kwargs={'pk': Book.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('book-detail', kwargs={'pk': Book.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_detail.html')

    def test_context_data(self):
        response = self.client.get(reverse('book-detail', kwargs={'pk': Book.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book'].id, 1)
        self.assertEqual(response.context['book'].title, 'Book Title')
        self.assertEqual(response.context['book'].author.first_name, 'John')
        self.assertEqual(response.context['book'].author.last_name, 'Smith')
        self.assertEqual(response.context['book'].summary, 'My book summary')
        self.assertEqual(response.context['book'].isbn, 'ABCDEFG')
        self.assertEqual(response.context['book'].language.name, 'English')
        self.assertEqual(response.context['book'].genre.count(), 3)
        self.assertEqual(response.context['book'].bookinstance_set.count(), 4)
        for book_copy in response.context['book'].bookinstance_set.all():
            self.assertTrue(book_copy.status in ['m', 'o', 'a', 'r'])
            self.assertFalse(book_copy.is_overdue)

class BookInstanceListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre1 = Genre.objects.create(name='Fantasy')
        test_genre2 = Genre.objects.create(name='Fiction')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 8
        for book_copy in range(number_of_book_copies):
            return_date = datetime.date.today() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'o'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_uses_correct_template(self):
        response = self.client.get(reverse('bookinstances'))
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/bookinstance_list.html')

    def test_pages_ordered_by_due_date(self):
        response = self.client.get(reverse('bookinstances'))
        self.assertEqual(response.status_code, 200)
        # Confirm that of the items, only 5 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 5)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back

    def test_pagination_is_five(self):
        response = self.client.get(reverse('bookinstances'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['bookinstance_list']), 5)

    def test_lists_all_book_instances(self):
        # Get second page and confirm it has (exactly) 3 remaining items (8 b.i. - 5 of first page)
        response = self.client.get(reverse('bookinstances')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['bookinstance_list']), 3)

class BookInstanceDetailViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')

        test_user.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre1 = Genre.objects.create(name='Fantasy')
        test_genre2 = Genre.objects.create(name='Fiction')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a book instance
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        the_borrower = test_user
        status = 'o'
        BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=the_borrower,
            status=status,
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/catalog/bookinstance/{BookInstance.objects.all()[0].pk}')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('bookinstance-detail', kwargs={'pk': BookInstance.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('bookinstance-detail', kwargs={'pk': BookInstance.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_detail.html')

    def test_context_data(self):
        response = self.client.get(reverse('bookinstance-detail', kwargs={'pk': BookInstance.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['bookinstance'].pk, BookInstance.objects.all()[0].pk)
        self.assertEqual(response.context['bookinstance'].book.title, 'Book Title')
        self.assertEqual(response.context['bookinstance'].book.author.first_name, 'John')
        self.assertEqual(response.context['bookinstance'].book.author.last_name, 'Smith')
        self.assertEqual(response.context['bookinstance'].book.summary, 'My book summary')
        self.assertEqual(response.context['bookinstance'].book.isbn, 'ABCDEFG')
        self.assertEqual(response.context['bookinstance'].book.language.name, 'English')
        self.assertEqual(response.context['bookinstance'].book.genre.count(), 2)
        self.assertEqual(response.context['bookinstance'].status, 'o')
        self.assertEqual(response.context['bookinstance'].due_back, datetime.date.today() + datetime.timedelta(days=5))
        self.assertEqual(response.context['bookinstance'].imprint, 'Unlikely Imprint, 2016')

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) 3 remaining items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['author_list']), 3)

class AuthorDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):# Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
            genre_objects_for_book = Genre.objects.all()
            # Create a language :
            test_language = Language.objects.create(name='English')
            # Create an author :
            date_of_birth = datetime.date(1932, 5, 17)
            date_of_death = datetime.date(2007, 11, 23)
            test_author = Author.objects.create(
            first_name='John',
            last_name='Smith',
            date_of_birth=date_of_birth,
            date_of_death=date_of_death,
            )
            # Create a book
            test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
            )
            test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
            test_book.save()
            # Create 4 book instances (copies) of that book
            number_of_book_copies = 4
            for book_copy in range(number_of_book_copies):
                return_date = datetime.date.today() + datetime.timedelta(days=book_copy+1)
                status = ['m', 'o', 'a', 'r'][book_copy]
                BookInstance.objects.create(
                book=test_book,
                imprint=f'Unlikely Imprint, 2016 #{book_copy}',
                due_back=return_date,
                status=status,
                )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/author/1')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('author-detail', kwargs={'pk': Author.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('author-detail', kwargs={'pk': Author.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_detail.html')

    def test_context_data(self):
        response = self.client.get(reverse('author-detail', kwargs={'pk': Author.objects.all()[0].pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'].id, 1)
        self.assertEqual(response.context['author'].first_name, 'John')
        self.assertEqual(response.context['author'].last_name, 'Smith')
        self.assertEqual(response.context['author'].date_of_birth, datetime.date(1932, 5, 17))
        self.assertEqual(response.context['author'].date_of_death, datetime.date(2007, 11, 23))
        self.assertEqual(response.context['author'].book_set.count(), 1)
        self.assertEqual(response.context['author'].book_set.all()[0].bookinstance_set.count(), 4)
        self.assertEqual(response.context['author'].book_set.all()[0].title, 'Book Title')
        self.assertEqual(response.context['author'].book_set.all()[0].summary, 'My book summary')

class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change the first ten books(instances) to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back

    def test_pagination_is_ten(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['bookinstance_list']), 10)

    def test_lists_all_book_instances(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        # Get second page and confirm it has (exactly) 5 remaining items (30 b.i. / 2 users - 10 of first page)
        response = self.client.get(reverse('my-borrowed')+'?page=2')
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['bookinstance_list']), 5)

class AllBorrowedListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 16 BookInstance objects
        number_of_book_copies = 16
        for book_copy in range(number_of_book_copies):
            return_date = datetime.date.today() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('all-borrowed'))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_all_borrowed_books(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))
        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_all.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser2')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change the first ten books(instances) to be on loan
        books = BookInstance.objects.all()[:10]
        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have 10 borrowed books in the list
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 10)
        # Confirm all books are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(bookitem.status, 'o')

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back

    def test_pagination_is_ten(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['bookinstance_list']), 10)

    def test_lists_all_book_instances(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        # Get second page and confirm it has (exactly) 6 remaining items (16 - 10 of first page)
        response = self.client.get(reverse('all-borrowed')+'?page=2')
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['bookinstance_list']), 6)

class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk}))

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UUID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk':test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['due_back'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk':self.test_bookinstance1.pk,}), {'due_back': valid_date_in_future})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}), {'due_back': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', _('Invalid date - passed date'))

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk}), {'due_back': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', _('Invalid date - more than 4 weeks ahead'))

class AuthorCreateTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit author data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_successfull_author_creation(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # Create form data
        first_name = 'John'
        last_name = 'Smith'
        date_of_birth = datetime.date(1932, 5, 17)
        date_of_death = datetime.date(2007, 11, 23)
        response = self.client.post(reverse('author-create'), {
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'date_of_death': date_of_death
        })
        self.assertEqual(response.status_code, 302)

    def test_author_creation_with_invalid_dates(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # Create form data
        first_name = 'John'
        last_name = 'Smith'
        date_of_birth = 'a long time ago'
        date_of_death = 'not yet'
        response = self.client.post(reverse('author-create'), {
            'first_name': first_name,
            'last_name': last_name,
            'date_of_birth': date_of_birth,
            'date_of_death': date_of_death
        })
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'date_of_birth', 'Enter a valid date.')
        self.assertFormError(response, 'form', 'date_of_death', 'Enter a valid date.')

class AuthorUpdateTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit author data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        self.test_author = Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/1/update/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author-update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_successfull_author_update(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # new form data
        date_of_birth = datetime.date(1958, 5, 17)
        response = self.client.post(reverse('author-update', kwargs={'pk': self.test_author.pk}), {
            'first_name': 'Johnny',
            'date_of_birth': date_of_birth,
        })
        self.assertEqual(response.status_code, 200)

    def test_author_update_with_invalid_dates(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-update', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # new form data, invalid
        date_of_birth = 'a long time ago'
        date_of_death = 'not yet'
        response = self.client.post(reverse('author-update', kwargs={'pk': self.test_author.pk}), {
            'first_name': 'Johnny',
            'date_of_birth': date_of_birth,
            'date_of_death': date_of_death,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'date_of_birth', 'Enter a valid date.')
        self.assertFormError(response, 'form', 'date_of_death', 'Enter a valid date.')

class AuthorDeleteTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit author data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        self.test_author = Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author-delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/1/delete')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author-delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_confirm_delete.html')

    def test_successfull_author_delete(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author-delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('author-delete', kwargs={'pk': self.test_author.pk}))
        self.assertEqual(response.status_code, 302)

class BookCreateTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit book data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        self.genre_objects_for_book = Genre.objects.all()
        # Create a language :
        self.test_language = Language.objects.create(name='English')
        # Create an author :
        self.test_author = Author.objects.create(first_name='John', last_name='Smith')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/book/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

    def test_successfull_book_creation(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('book-create'), {
            'title': 'My Book',
            'author': self.test_author,
            'summary': 'My Book Summary',
            'isbn': 'ABCDEFG',
            'genre': self.genre_objects_for_book,
            'language': self.test_language,
        })
        self.assertEqual(response.status_code, 200)

    def test_book_creation_with_invalid_data(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('book-create'), {
            'title': 'My Book',
            'author': self.test_author,
            'summary': 'My Book Summary',
            'isbn': '12345678901234', # Too long, 14 characters
            'genre': self.genre_objects_for_book,
            'language': self.test_language,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'isbn', 'Ensure this value has at most 13 characters (it has 14).')

class BookUpdateTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit book data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create a language :
        test_language = Language.objects.create(name='English')
        # Create an author :
        test_author = Author.objects.create(first_name='John', last_name='Smith')

        # Create a book
        self.test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Set genre as a post-step
        self.test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        self.test_book.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/book/1/update/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

    def test_successfull_book_update(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # post with new data
        response = self.client.post(reverse('book-update', kwargs={'pk': self.test_book.pk}), {
            'title':'Another Title',
            'summary': 'This book is very good',
            'isbn': '0123456',
            'author': Author.objects.create(first_name='Bruce', last_name='Willis', date_of_birth=datetime.date(1958, 4, 9)),
            'language': Language.objects.create(name='Japanese'),
        })
        self.assertEqual(response.status_code, 200)

    def test_book_update_with_invalid_dates(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # post with new (wrong) data
        response = self.client.post(reverse('book-update', kwargs={'pk': self.test_book.pk}), {
            'title': 'Another Title',
            'summary': 'This book is very good',
            'isbn': '12345678901234', # Wrong : 14 characters
            'author': Author.objects.create(first_name='Bruce', last_name='Willis', date_of_birth=datetime.date(1958, 4, 9)),
            'language': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'isbn', 'Ensure this value has at most 13 characters (it has 14).')

class BookDeleteTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit book data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create a language :
        test_language = Language.objects.create(name='English')
        # Create an author :
        test_author = Author.objects.create(first_name='John', last_name='Smith')

        # Create a book
        self.test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Set genre as a post-step
        self.test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        self.test_book.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/book/1/delete')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_confirm_delete.html')

    def test_successfull_book_delete(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('book-delete', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 302)

class BookInstanceCreateTest(TestCase):
    def setUp(self):
        # Create three users, two for login/permission tests, one as test borrower
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        self.test_borrower = User.objects.create_user(username='Toto', password='thepasswordoftoto')

        test_user1.save()
        test_user2.save()
        self.test_borrower.save()

        permission = Permission.objects.get(name='Can edit book data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create a language :
        test_book_language = Language.objects.create(name='English')
        self.test_bookinstance_language = Language.objects.create(name='Chinese')
        # Create an author :
        test_author = Author.objects.create(first_name='John', last_name='Smith')

        # Create a book
        self.test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_book_language,
        )

        # Set genre as a post-step
        self.test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        self.test_book.save()

        self.test_due_back = datetime.date.today() + datetime.timedelta(days=5)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('bookinstance-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/bookinstance/create/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('bookinstance-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')

    def test_successfull_bookinstance_creation(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('bookinstance-create'), {
            'book': self.test_book,
            'language': self.test_bookinstance_language,
            'imprint': 'Fabulous copy',
            'due_back': self.test_due_back,
            'status': 'o',
            'borrower': self.test_borrower,
        })
        self.assertEqual(response.status_code, 200)

    def test_bookinstance_creation_with_invalid_data(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-create'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('bookinstance-create'), {
            'book': self.test_book,
            'language': self.test_bookinstance_language,
            'imprint': 'Fabulous copy',
            'due_back': 'now!',
            'status': 'o',
            'borrower': self.test_borrower,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', 'Enter a valid date.')

class BookInstanceUpdateTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit book data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create a language :
        test_language1 = Language.objects.create(name='English')
        test_language2 = Language.objects.create(name='Italian')
        # Create an author :
        test_author = Author.objects.create(first_name='John', last_name='Smith')

        # Create a book
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language1,
        )

        # Set genre as a post-step
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a book instance (copy)
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance = BookInstance.objects.create(
            book=test_book,
            language=test_language2,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/catalog/bookinstance/{self.test_bookinstance.pk}/update/')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')

    def test_successfull_bookinstance_update(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # post with new data
        response = self.client.post(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}), {
            'due_back': '',
            'status': 'a',
            'borrower': '',
        })
        self.assertEqual(response.status_code, 200)

    def test_bookinstance_update_with_invalid_data(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # post with new (wrong) data
        response = self.client.post(reverse('bookinstance-update', kwargs={'pk': self.test_bookinstance.pk}), {
            'due_back': 'Right now!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', 'Enter a valid date.')

class BookInstanceDeleteTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Can edit book data')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create 3 genres :
        number_of_genres = 3
        for genre_id in range(number_of_genres):
            Genre.objects.create(name=f'Genre {genre_id}')
        genre_objects_for_book = Genre.objects.all()
        # Create a language :
        test_language1 = Language.objects.create(name='English')
        test_language2 = Language.objects.create(name='Italian')
        # Create an author :
        test_author = Author.objects.create(first_name='John', last_name='Smith')

        # Create a book
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language1,
        )

        # Set genre as a post-step
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a book instance (copy)
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance = BookInstance.objects.create(
            book=test_book,
            language=test_language2,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('bookinstance-delete', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/catalog/bookinstance/{self.test_bookinstance.pk}/delete')

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('bookinstance-delete', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-delete', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-delete', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_confirm_delete.html')

    def test_successfull_bookinstance_delete(self):
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('bookinstance-delete', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('bookinstance-delete', kwargs={'pk': self.test_bookinstance.pk}))
        self.assertEqual(response.status_code, 302)
