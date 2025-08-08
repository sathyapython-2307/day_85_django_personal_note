
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Note
from .forms import UserRegisterForm, NoteForm
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages

class RegisterView(View):
	def get(self, request):
		if request.user.is_authenticated:
			return redirect('note-list')
		form = UserRegisterForm()
		return render(request, 'registration/register.html', {'form': form})

	def post(self, request):
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = True
			user.save()
			messages.success(request, 'Registration successful! You can now log in.')
			return redirect('login')
		messages.error(request, 'Registration failed. Please correct the errors below.')
		return render(request, 'registration/register.html', {'form': form})

class NoteListView(LoginRequiredMixin, ListView):
	model = Note
	template_name = 'notes/note_list.html'
	context_object_name = 'notes'

	def get_queryset(self):
		if self.request.user.is_superuser:
			return Note.objects.all().order_by('-created_at')
		return Note.objects.filter(owner=self.request.user).order_by('-created_at')

class NoteDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
	model = Note
	template_name = 'notes/note_detail.html'

	def test_func(self):
		note = self.get_object()
		return self.request.user.is_superuser or note.owner == self.request.user

class NoteCreateView(LoginRequiredMixin, CreateView):
	model = Note
	form_class = NoteForm
	template_name = 'notes/note_form.html'
	success_url = reverse_lazy('note-list')

	def form_valid(self, form):
		form.instance.owner = self.request.user
		return super().form_valid(form)

class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Note
	form_class = NoteForm
	template_name = 'notes/note_form.html'
	success_url = reverse_lazy('note-list')

	def test_func(self):
		note = self.get_object()
		return note.owner == self.request.user

class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Note
	template_name = 'notes/note_confirm_delete.html'
	success_url = reverse_lazy('note-list')

	def test_func(self):
		note = self.get_object()
		return note.owner == self.request.user
