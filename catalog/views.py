from operator import contains
from django.shortcuts import render, Http404, get_object_or_404
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


from .models import Book, Author, BookInstance, Genre, Language

# Create your views here.
def index(request):
    
    #generating count of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    #available books (status = 'a')
    num_Instances_avaialable = BookInstance.objects.filter(status__exact = 'a').count()
    selected_genres = Genre.objects.filter(name__icontains = 'fiction').count()
    selected_books = Book.objects.filter(title__icontains = 'touch').count()
    
    ##here all(),  is implied by default
    num_authors = Author.objects.count()
    
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_Instances_avaialable,
        'num_authors': num_authors,
        'selected_genres': selected_genres,
        'selected_books': selected_books,
        'num_visits': num_visits,
        }
    
    #rendering html template with the data in the context
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    context_object_name = 'book_list'
    #your own name for the list as a template variable
    queryset = Book.objects.all()
    template_name = 'catalog/book_list.html'

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    context_object_name = 'author_list'
    #your own name for the list as a template variable
    queryset = Author.objects.all()
    template_name = 'catalog/author_list.html'
    
class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    
class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/borrowed_booklist.html'
    paginate_by = 2

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

  
#function based view
#from django.contrib.auth.decorators import login_required

#@login_required
#def my_view(request):
#def book_detail_view(request, primary_key):
#    try:
#        book = Book.objects.get(pk=primary_key)
#    except Book.DoesNotExist:
#        raise Http404('Book does not exist')
#
#    return render(request, 'catalog/book_detail.html', context={'book': book})

#or use this
#def book_detail_view(request, primary_key):
   # book = get_object_or_404(Book, pk=primary_key)
   # return render(request, 'catalog/book_detail.html', context={'book': book})
   
   
class MyView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/all_borrowed.html'
   
    permission_required = ('catalog.can_mark_returned',)

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact = 'o')

   
import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew.html', context)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class AuthorCreate(PermissionRequiredMixin,CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    
    
class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    

class BookUpdate(UpdateView):
    model = Book 
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')