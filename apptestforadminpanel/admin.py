
from django.contrib import admin, messages
from django import forms
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Author, Book, Genre
from django.utils.translation import ngettext
import re # regex
from faker import Faker
import random as rd

# Création / récupération des groupes 

view_group, created = Group.objects.get_or_create(name="Lecture")
deploy_group, created = Group.objects.get_or_create(name="Deploiement")
support_group, created = Group.objects.get_or_create(name="Support")
administrator_group, created = Group.objects.get_or_create(name="Administrateur")

# On récupère les données des modèles de l'app 
book_content_type = ContentType.objects.get_for_model(Book)
author_content_type = ContentType.objects.get_for_model(Author)
genre_content_type = ContentType.objects.get_for_model(Genre)

# ALTERNATIVE : Si on veut tous les modèles de l'app :
# content_type = apps.get_models()

# On récupère les permissions pour chaque modèle (CRUD de chaque modèle)
post_permission = Permission.objects.filter(content_type__in=[book_content_type, author_content_type, genre_content_type])

# print([perm.codename for perm in post_permission]) # DEBUG
# => ['add_post', 'change_post', 'delete_post', 'view_post']

# Attribution des permissions 

for perm in post_permission:
	if re.search("^delete_.*$", perm.codename):
		deploy_group.permissions.add(perm)
	elif re.search("^change_.*$", perm.codename):
		support_group.permissions.add(perm)
		deploy_group.permissions.add(perm)
	elif re.search("^add_.*$", perm.codename):
		support_group.permissions.add(perm)
	elif re.search("^view_.*$", perm.codename):
		view_group.permissions.add(perm)
		support_group.permissions.add(perm)
		deploy_group.permissions.add(perm)

# Création d'un user

#user = User.objects.create_user(username='john',
#                                 email='jlennon@beatles.com',
#                                 password='glass onion')

# Obtention d'un user

user = User.objects.get(username="john")
user.groups.add(view_group)  # Add the user to the Lecture group

# Register your models here.


# Configuration d'actions personnalisés
@admin.action(description="Changer la description par action")
def actiondonnee(modeladmin, request, queryset):

	# Changement d'un champ des lignes sélectionnées
	donnee_changee = queryset.update(description="j'ai changé avec une action",)
	
	# 'Toast' pour succès (dans ce cas)
	modeladmin.message_user(
            request,
            ngettext(
                "%d description a bien été mis à jour.",
                "%d description ont bien été mises à jour.",
                donnee_changee,
            )
            % donnee_changee,
            messages.SUCCESS,
        )

@admin.action(description="Fais quelque chose [B]")
def seconde_action_donnee(modeladmin, request, queryset):
	pass

@admin.action(description="Fais autre chose [C]")
def troisieme_action_donnee(modeladmin, request, queryset):
	pass
	
@admin.action(description="Fais une autre action [D]")
def quatrieme_action_donnee(modeladmin, request, queryset):
	pass
	

class AdminAuthorForm(forms.ModelForm):

	# On spécifie sur quel modèle on se base
	model = Author
	class Meta:
		# Affichage des champs dans la page d'ajout / edit
		fields = "__all__"

class ViewerAuthorForm(forms.ModelForm):
	model = Author
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		disable_fields(self.fields, ['name', 'surname', 'age', 'tel', 'mail', 'x',])

class DeployAuthorForm(forms.ModelForm):
	model = Author
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		disable_fields(self.fields, ['tel', 'mail', 'x',])

class SupportAuthorForm(forms.ModelForm):
	model = Author
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		disable_fields(self.fields, ['name', 'surname', 'age',])


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

	# Permet d'afficher ce que renvoi le __str__ sur le panel admin
	list_display = ['__str__']
	# Gère la pagination
	list_per_page = 25

	actions = [actiondonnee, seconde_action_donnee, 
			   troisieme_action_donnee, quatrieme_action_donnee]

	def get_actions(self, request):
		actions = super().get_actions(request)
		user_group = get_user_group(request)
		
		# Pour chaque groupe, on enlève les actions non désirés
		if user_group == "Deploiement":
			if "quatrieme_action_donnee" in actions:
				del actions["quatrieme_action_donnee"]

		elif user_group == "Support":
			if "delete_selected" in actions:
				del actions["delete_selected"]
			if "troisieme_action_donnee" in actions:
				del actions["troisieme_action_donnee"]

		elif user_group == "Lecture":
			if "delete_selected" in actions:
				del actions["delete_selected"]
			if "seconde_action_donnee" in actions:
				del actions["seconde_action_donnee"]
			if "troisieme_action_donnee" in actions:
				del actions["troisieme_action_donnee"]
		elif user_group != "Administrateur":
			# Utilisateur sans droits
			return {} # Pas d'actions
		return actions

	# Redéfini le formulaire (ici en fonction des groupes)
	def get_form(self, request, obj=None, **kwargs):

		user_group = "" # Initialisation à vide

		# Récupération du groupe du user
		if (len(list(request.user.groups.all()))> 0 ):
			user_group = list(request.user.groups.all())[0].__str__()
			
		if request.user.is_superuser:
			kwargs['form'] = AdminAuthorForm
		elif (user_group == "Deploiement"):
			kwargs['form'] = DeployAuthorForm
		elif (user_group == "Support"):
			kwargs['form'] = SupportAuthorForm
		else :
			kwargs['form'] = ViewerAuthorForm			
		return super().get_form(request, obj, **kwargs)

	# Crée des sections de champs (pour add et edit)
	fieldsets = [
		(
			None, 
			{
				"fields": ["name", "surname", "age"],
			}
		),
		(
			"Données supplémentaires", 
			{
				"fields": ["tel", "mail"], "classes": ["collapse"], "description": "Données supplémentaires à renseigner",
			}
		),
		(
			"Nombres test", 
			{
				"fields": ["x", "xTimesTwo"], "classes": ["collapse"]
			}
		),
	]

	# Désactive à l'édition les champs spécifiés
	readonly_fields = ["xTimesTwo"]
	
	# Spécifie quel(s) champ(s) sera/seront impacté(s) par la barre de recherche
	search_fields = ["name"]

	# [CONSEILLÉ] -> Implémente la recherche avec les données du search_fields
	def get_search_results(self, request, queryset, search_term): 
		queryset, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )

		queryset |= self.model.objects.filter(name=search_term)
		return queryset, may_have_duplicates


# Permet de gérer les formulaires (add et edit) // Encore à voir
class AdminBookForm(forms.ModelForm):
	model = Book
	class Meta:
		# Indique qu'on veut tous les champs du modèle
		fields = "__all__"

class ViewerBookForm(forms.ModelForm):
	model = Book
	class Meta:
		# Affichage des champs dans la page d'ajout / edit
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Liste des champs que tu veux rendre non modifiables
		
		disable_fields(self.fields, ['nb_selled_books', 'author', 'title'])

class NoGroupsForm(forms.ModelForm):
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Liste des champs que tu veux rendre non modifiables
		disable_fields(self.fields, list(self.fields.keys()))

class DeployAndSupportBookForm(forms.ModelForm):
	model = Book
	class Meta:
		# Affichage des champs dans la page d'ajout / edit
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Liste des champs que tu veux rendre non modifiables
		disable_fields(self.fields, ['nb_selled_books', 'description'])


		
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

	# Champs affichés
	list_display = ['titre_colore', 'description', 'author', "nb_selled_books"]

	# Spécifie quelles actions sont liées à la page admin associée
	actions = [actiondonnee, seconde_action_donnee]

	def get_form(self, request, obj=None, **kwargs):

		# Récupération du groupe du user
		user_group = get_user_group(request)

		if user_group is None: # L'utilisateur n'a aucun groupe
			kwargs['form'] = NoGroupsForm
		elif request.user.is_superuser: # Vérifie si user est root
			kwargs['form'] = AdminBookForm
		elif (user_group == "Deploiement" or user_group == "Support"): # Vérifie les autres rôles
			kwargs['form'] = DeployAndSupportBookForm
		else :
			kwargs['form'] = ViewerBookForm			
		return super().get_form(request, obj, **kwargs)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

	# Page perso html pour ajout / modification d'un elt
	# change_form_template = "/home/loris/romain_porcer/django_tests/tutorial/project_test/apptestforadminpanel/templates/admin/apptestforadminpanel/adminPanelTest.html"


	filter_horizontal = ["linked_books"]

	# Sert à modifier tout des interfaces CRUD admin
	# Code de la doc  https://docs.djangoproject.com/fr/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.change_view

#	def get_osm_info(self):
#       # ...
#		pass
#	
#	def change_view(self, request, object_id, form_url='', extra_context=None):
#		extra_context = extra_context or {}
#		extra_context['osm_data'] = self.get_osm_info()
#		return super().change_view(
#            request, object_id, form_url, extra_context=extra_context,
#        )
	
#	class Media:  # Si on utilise du css, js, etc... dans la vue, le spécifier ici
#		css = {
#			"all": ["style_exemple.css"],
#		}
#		js = ["script_exemple.js"]

# A voir :
# radio_fields = {"group": admin.VERTICAL}  # Pour admin


##########################################################################
#                      GENERATION DE DONNEES FACTICES					 

fake = Faker(locale="fr_FR")

NB_AUTEURS = 100
NB_GENRES = 10
NB_LIVRES = 200

def create_authors():
	authors = []
	for r in range(NB_AUTEURS):
		fake_name = fake.name().split(' ')
		fname = fake_name[1]
		fsurname = fake_name[0]
		fage = fake.numerify(text="%%")
		ftel = fake.phone_number()
		fmail = fake.email()
		fx = fake.numerify(text="%%%")
		author = Author.objects.create(
			name=fname,
			surname=fsurname,
			age=fage,
			tel=ftel,
			mail = fmail,
			x=fx
		)
		authors.append(author)
	return authors

def create_books(authors):
	books = []
	for r in range(NB_AUTEURS):
		ftitle = fake.word()
		fdescription = fake.sentence()
		fselled_books = fake.numerify(text="%%%%")
		fauthor = rd.choice(authors)
		book = Book.objects.create(
			title = ftitle,
			description = fdescription,
			nb_selled_books = fselled_books,
			author = fauthor
		)
		books.append(book)
	return books


def create_genres(books):
	genres = []
	for r in range(NB_AUTEURS):
		fname = fake.job()
		flinked_books = rd.choices(books, k = 20)

		genre = Genre.objects.create(
			name=fname,
		)
		genre.linked_books.set(flinked_books)

		genres.append(genre)
	return genres

authors = create_authors()
books = create_books(authors)
create_genres(books)
#																		
##########################################################################


## A DEPLACER DANS utils.py :

def disable_fields(form_fields, uneditable_fields):
	""" Description

		:type form_fields: List
		:param form_fields: your form's fields
		
		:type uneditable_fields: List
		:param uneditable_fields: the specifics fields you don't want to be editable
	
		:rtype: void
		:returns: nothing
	""" 

	form_fields_keys = list(form_fields.keys())

	for	champ in uneditable_fields:
		if champ in form_fields_keys:
			form_fields[champ].disabled = True
			form_fields[champ].widget.attrs.update({ 'style': 'background-color:#eee !important; color:#888 !important'})


def get_user_group(request):
	
	""" Description
	:type request: HttpRequest
	:param request: request made by the user, when asking 
					for something from the django-admin panel

	:rtype: String|None
	:returns: The current UNIQUE user group or None if he don't have one
	"""

	if (len(list(request.user.groups.all())) == 0):
		return None
	return list(request.user.groups.all())[0].__str__()
##