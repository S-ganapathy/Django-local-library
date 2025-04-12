from typing import Any
import datetime
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


# Create your views here.
@login_required
def index(request):
    """ View funtion for home page of the site."""

    num_books=Book.objects.all().count()
    num_instance=BookInstance.objects.all().count()
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()
    num_genre=Genre.objects.all().count()
    num_atom_books=Book.objects.filter(title__contains="Atom").count()

    '''visit counter using session'''
    num_visit=request.session.get("num_visitor",0)
    num_visit+=1
    request.session['num_visitor']=num_visit

    context={
        'num_books':num_books,
        'num_instance':num_instance,
        'num_instances_available':num_instances_available,
        'num_authors':num_authors,
        'num_genre':num_genre,
        "num_atom_books":num_atom_books,
        "num_visit":num_visit
    }

    return render(request,'index.html',context=context)

class BookListView(LoginRequiredMixin,generic.ListView):
    model=Book
    paginate_by=2
    context_object_name='book_list'
    template_name='catalog/book_list.html'

    def get_queryset(self):
        return Book.objects.all()
    
    def get_context_data(self, **kwargs):
        context=super(BookListView,self).get_context_data(**kwargs)
        context['some_additonal_data']='this is just some data'
        return context

class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model=Book

class AuthorListView(LoginRequiredMixin,generic.ListView):
    model=Author
    paginate_by=10
    context_object_name='author_list'
    template_name='catalog/author_list.html'

    def get_queryset(self):
        return Author.objects.all()
    
class AuthorDetailView(LoginRequiredMixin,generic.DetailView):
    model=Author


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model=BookInstance
    template_name='catalog/bookinstance_list_borrowed_user.html'

    def get_queryset(self):
        return(
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )


class BorrowedListView(LoginRequiredMixin,generic.ListView): 
    # permission_required=('catalog.can_view_borrowed','catalog.staff_level') permissionrequiredmixin
    model=BookInstance
    context_object_name="borrowed_list"
    template_name='catalog/borrowed_list.html'

    def get_queryset(self):
        return(
            BookInstance.objects.filter(status__exact='o').order_by('due_back')
        )
@login_required
@permission_required('catalog.staff_level')
def renew_book_librarian(request,pk):
    book_instance=get_object_or_404(BookInstance,pk=pk)

    if request.method=='POST':
        form = RenewBookForm(request.POST)

        if(form.is_valid()):
            book_instance.due_back=form.cleaned_data['renewal_date']
            book_instance.save()
        return(HttpResponseRedirect(reverse('all_borrowed')))
    
    else:
        proposed_renewal_date=datetime.date.today()+datetime.timedelta(weeks=3)
        form=RenewBookForm(initial={'renewal_date':proposed_renewal_date})
        context={'form':form,
                 'book_instance':book_instance}
        
        return render(request,'catalog/book_renew_librarian.html',context)
    


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023','date_of_birth':'11/07/1967'}
    permission_required = 'catalog.staff_level'

    def form_valid(self,form):
        dob=form.cleaned_data['date_of_birth']
        dod=form.cleaned_data['date_of_death']

        if dob and dod and dob > dod:
            form.add_error('date_of_birth','Birth date cannot be after death date')
            return self.form_invalid(form)
        return super().form_valid(form)


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.staff_level'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.staff_level'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

class BookCreate(PermissionRequiredMixin,CreateView):
    model=Book
    fields='__all__'
    permission_required='catalog.staff_level'

class BookUpdate(PermissionRequiredMixin,UpdateView):
    model=Book
    fields='__all__'
    permission_required='catalog.staff_level'

class BookDelete(PermissionRequiredMixin,DeleteView):
    model=Book
    success_url=reverse_lazy("book-detail")
    permission_required="catalog.staff_level"

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )
