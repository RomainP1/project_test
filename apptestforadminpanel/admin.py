from faker import Faker
from import_export import resources
from django.contrib import admin, messages
from django import forms
from django.shortcuts import redirect, render
from django_admin_inline_paginator.admin import TabularInlinePaginated
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Author, Book, Genre, RelationBookGenre, Review, testToValidateData
from django.utils.translation import ngettext
from django.utils.html import format_html
import re # regex
import random as rd
from django.urls import reverse
from django.utils.http import urlencode
import csv
from import_export.admin import ImportExportModelAdmin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.http import HttpResponseRedirect


## A DEPLACER DANS utils.py :

def disable_fields(form_fields, editable_fields=[]):
	""" Description

		:type form_fields: List
		:param form_fields: your form's fields
		
		:type editable_fields: List
		:param editable_fields: the specifics fields you want to be editable
	
		:rtype: void
		:returns: nothing
	""" 

	form_fields_keys = list(form_fields.keys())

	for champ in form_fields_keys:
		if champ not in editable_fields:
			form_fields[champ].disabled = True
			form_fields[champ].widget.attrs.update({ 'style': 'background-color:#eee !important; color:#888 !important'})

#	for	champ in uneditable_fields:
#		if champ in form_fields_keys:
#			form_fields[champ].disabled = True
#			form_fields[champ].widget.attrs.update({ 'style': 'background-color:#eee !important; color:#888 !important'})


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

########################### ATTENTION #############################
# Si la base de données est recréée, il faut impérativement
# que les lignes concernant la création / gestion des groupes
# utilisateurs soient enlevés du code
###################################################################

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
models_permissions = Permission.objects.filter(content_type__in=[book_content_type, author_content_type, genre_content_type])

# print([perm.codename for perm in model_permission]) # DEBUG
# => ['add_model', 'change_model', 'delete_model', 'view_model']

# Attribution des permissions 

for perm in models_permissions:
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

# user = User.objects.get(username="john")
# user.groups.add(view_group)  # Add the user to the Lecture group



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

@admin.action(description="Modifier le livre de la revue")
def modify_parent_type(modeladmin, request, queryset):
	
	# Les données à modifier sont dans le queryset

	# Code conseillé par la doc : https://docs.djangoproject.com/fr/3.2/ref/contrib/admin/actions/
	selected = queryset.values_list('pk', flat=True)
	ct = ContentType.objects.get_for_model(queryset.model)

	# ? FIXME : Ne renvoi pas sur le form => Gérer urls dans urls.py

	return redirect('/admin/change_parent_type?ct=%s&ids=%s' % (
        ct.pk,
        ','.join(str(pk) for pk in selected),
    ))

def list_filter_factory(title_p="", parameter_name_p=""):

	""" Description : A little factory (not really a real one) made to
					  pass parameters into a ListFilter, in order to
					  make it more reusable

		:type title_p: String 
		:param title_p: The name to display over the filter
	
		:type parameter_name_p: String
		:param parameter_name_p: The filter name when you click on a filter element
	
		:rtype: ListFilter
		:returns: A customized ListFilter
		"""
	class ListFilter(admin.SimpleListFilter):

		title = title_p
		parameter_name = parameter_name_p

		# Cette template de list-filter sert à gérer un affichage plus poussé
		template = "/home/loris/romain_porcer/django_tests/tutorial/project_test/apptestforadminpanel/templates/admin/apptestforadminpanel/customFIlterReview.html"
		
		# Gère les données de la liste
		def lookups(self, request, model_admin):
			# Renvoi une liste de tuples : (idDonnee, donneeAAfficher)
			return [(str(cat.pk), str(cat)) for cat in Book.objects.all()] 
		

		# Gère les clics sur les items de la liste
		def queryset(self, request, queryset):
			lookup = {parameter_name_p : self.value()} # Permet de généraliser la FK associé au filtre
			if self.value():
				return queryset.filter(**lookup) # ! COMPRENDRE COMMENT FONCTIONNE CETTE PARTIE
			return queryset

	return ListFilter



class AuthorResource(resources.ModelResource):

    class Meta:
        model = Author

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
		
		disable_fields(self.fields)

class DeployAuthorForm(forms.ModelForm):
	model = Author
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		disable_fields(self.fields, ['name', 'surname', 'age',])

class SupportAuthorForm(forms.ModelForm):
	model = Author
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		disable_fields(self.fields, ['tel', 'mail', 'x',])

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
		
		disable_fields(self.fields, ['description',])

class NoGroupsForm(forms.ModelForm):
	class Meta:
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Liste des champs que tu veux rendre non modifiables
		disable_fields(self.fields)

class DeployAndSupportBookForm(forms.ModelForm):
	model = Book
	class Meta:
		# Affichage des champs dans la page d'ajout / edit
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Liste des champs que tu veux rendre non modifiables
		disable_fields(self.fields, ['title', 'author',])



class InlineBookAdmin(TabularInlinePaginated):

	model = Book
	form = ViewerBookForm
	per_page = 5

class InlineReviewsAdmin(TabularInlinePaginated):

	model = Review
	# form = ViewerReviewForm
	per_page = 5

class InlineRelationBookGenreAdmin(admin.TabularInline):
	model = RelationBookGenre
	extra = 0

	autocomplete_fields = ['book',]
	fields = ["book_title_display",]
	# book_title_display est un champ calculé donc il doit être
	# un paramètre de readonly_fields AUSSI
	readonly_fields = ["book_title_display",]
	def get_ordering(self, request):
		return None

	# Permet de n'afficher que les livres
	def get_queryset(self, request):
		query_set = super().get_queryset(request)
		return query_set.only("book")
	
	def book_title_display(self, obj):
	    return format_html(
            '<span style="color:rgb(92, 74, 63); font-size: 30px;">{}</span>',
            obj.book.title,) if obj.book else "-"

@admin.register(Author)
class AuthorAdmin(ImportExportModelAdmin):

	# Permet d'afficher ce que renvoi le __str__ sur le panel admin
	list_display = ['__str__']
	# Gère la pagination
	list_per_page = 25
	# change_list_template = "/home/loris/romain_porcer/django_tests/tutorial/project_test/apptestforadminpanel/templates/admin/apptestforadminpanel/authorAdminList.html"

	inlines = [InlineBookAdmin] # Liste des livres associés à l'auteur
	resource_classes = [AuthorResource] # Utile pour import/export données

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
		get_user_group(request)
			
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

		
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

	search_fields = ["title"]

	# Champs affichés
	list_display = ['titre_colore', 'description', 'author', "nb_selled_books", "view_genres_link", "view_reviews_link"]

	inlines = [InlineReviewsAdmin]

	# Définition d'un adminchamp du list_display
	def view_genres_link(self, obj):
		count = getattr(obj, "genre_set").count()
		
		# Permet de créer une URL pour rediriger sur les M2M
		url = (
			# Format général : "admin:<nom_app>_<obj_reference>_changelist"
            reverse("admin:apptestforadminpanel_genre_changelist")
            + "?" # Agit comme un WHERE
            + f"linked_books__id__exact={obj.id}"
        )
        
		return format_html('<a href="{}">{} Genres</a>', url, count)

	def view_reviews_link(self, obj):
		count = getattr(obj, "review_set").count()

		url = (
			# Format général : "admin:<nom_app>_<obj_reference>_changelist"
            reverse("admin:apptestforadminpanel_review_changelist")
            + "?" # Agit comme un WHERE
			# Format général : "<obj>__<elt_pour_where>"
            + f"reviewed_book__id__exact={obj.id}"
        )

		return format_html('<a href="{}">{} Critiques</a>', url, count)

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
	search_fields = ["title"]

	# On personnalise le filtre de la liste (celui à droite)
	lf = list_filter_factory("linked_books", "linked_books__id__exact")

	list_filter = (lf,)
	filter_horizontal = ["linked_books"]
	inlines = [InlineRelationBookGenreAdmin]


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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ["title", "description", "view_note_link", "view_reviewed_book_link",]
	list_per_page = 25

	lf = list_filter_factory("reviewed_book", "reviewed_book__id__exact")

	list_filter = (lf,)

	# On veut pouvoir changer de livre pour la revue
	actions = [modify_parent_type]
	
	# On crée une nouvelle façon d'afficher quelque chose sur la liste
	def view_note_link(self, obj):
		return format_html("<span style='color:#222'>{}/5</span>", obj.overall_note)

	def view_reviewed_book_link(self, obj):
		# Redirige sur la page du livre
		return format_html("<a href='../book/{}'>{}</a>", obj.reviewed_book.id, obj.reviewed_book.title)

	# On redéfini le champ de la liste
	view_note_link.short_description = "Note"
	view_reviewed_book_link.short_description = "Livre revu"

	def __str__(self):
		return self.title
	
admin.site.register(testToValidateData)

##########################################################################
#                      GENERATION DE DONNEES FACTICES					 

fake = Faker(locale="fr_FR")

NB_AUTEURS = 0
NB_LIVRES = 0
NB_GENRES = 0
NB_REVUES = 0

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
	for r in range(NB_LIVRES):
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
		book.save()
		books.append(book)
	return books


def create_genres(books):
	genres = []
	for r in range(NB_GENRES):
		fname = fake.job()
		flinked_books = rd.choices(books, k = 20)

		genre = Genre.objects.create(
			name=fname,
		)
		genre.linked_books.set(flinked_books)

		genres.append(genre)
	return genres


def create_reviews():
	reviews = []
	for r in range(NB_REVUES):
		ftitle = fake.word()
		fdescription = fake.text()
		foverall_note = rd.randint(1, 5)
		review = Review.objects.create(
			title = ftitle,
			description = fdescription,
			overall_note = foverall_note,
			reviewed_book = rd.choice(Book.objects.all())
		)

		review.save()

		reviews.append(review)
	return reviews


authors = create_authors()
books = create_books(authors)
create_genres(books)
create_reviews()
#																		
##########################################################################


# Données intéressantes

# formfield_overrides
# Virtual Scrolls
# FlexField