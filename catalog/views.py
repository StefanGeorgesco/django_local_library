import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

# Create your views here.

from catalog.models import Book, Author, BookInstance, Genre, Language

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    # Reserved books (status = 'r')
    num_instances_reserved = BookInstance.objects.filter(status__exact='r').count()
    # On loan books (status = 'o')
    num_instances_loan = BookInstance.objects.filter(status__exact='o').count()
    # On maintenance books (status = 'm')
    num_instances_maintenance = BookInstance.objects.filter(status__exact='m').count()

    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_languages = Language.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_instances_reserved': num_instances_reserved,
        'num_instances_loan': num_instances_loan,
        'num_instances_maintenance': num_instances_maintenance,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_languages': num_languages,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class BookInstanceListView(generic.ListView):
    model = BookInstance
    paginate_by = 5

class BookInstanceDetailView(generic.DetailView):
    model = BookInstance

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllBorrowedListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan with specific permission (granted to librarians)."""
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

from catalog.forms import RenewBookModelForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """ View function for renewing a specific BookInstance by librarian. """
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is Valid
        if form.is_valid():
            # Process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # Redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))
    # If this is a GET (or any other) method, create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    fields = '__all__'

class AuthorUpdate(PermissionRequiredMixin, generic.edit.UpdateView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    fields = '__all__'

class AuthorDelete(PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'catalog.can_edit_author'
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, generic.edit.UpdateView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'catalog.can_edit_book'
    model = Book
    success_url = reverse_lazy('books')

class BookInstanceCreate(PermissionRequiredMixin, generic.edit.CreateView):
    permission_required = 'catalog.can_edit_book'
    model = BookInstance
    fields = ['book', 'language', 'imprint', 'due_back', 'status', 'borrower']
    success_url = reverse_lazy('books')

class BookInstanceUpdate(PermissionRequiredMixin, generic.edit.UpdateView):
    permission_required = 'catalog.can_edit_book'
    model = BookInstance
    fields = ['book', 'language', 'imprint', 'due_back', 'status', 'borrower']
    success_url = reverse_lazy('books')

class BookInstanceDelete(PermissionRequiredMixin, generic.edit.DeleteView):
    permission_required = 'catalog.can_edit_book'
    model = BookInstance
    success_url = reverse_lazy('books')
