
from django.contrib import admin, messages
from django import forms
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Author, Book, Genre
from django.utils.translation import ngettext


view_group, created = Group.objects.get_or_create(name="Lecture")
deploy_group, created = Group.objects.get_or_create(name="Deploiement")
support_group, created = Group.objects.get_or_create(name="Support")


book_content_type = ContentType.objects.get_for_model(Book)
post_permission = Permission.objects.filter(content_type=book_content_type)

print([perm.codename for perm in post_permission])
# => ['add_post', 'change_post', 'delete_post', 'view_post']

for perm in post_permission:
	if perm.codename == "delete_post":
		deploy_group.permissions.add(perm)

	elif perm.codename == "change_post":
		support_group.permissions.add(perm)
		deploy_group.permissions.add(perm)
	elif perm.codename == "add_post":
		view_group.permissions.add(perm)
	else:
		view_group.permissions.add(perm)
		support_group.permissions.add(perm)
		deploy_group.permissions.add(perm)

#user = User.objects.create_user(username='john',
#                                 email='jlennon@beatles.com',
#                                 password='glass onion')

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

@admin.action(description="Fais quelque chose")
def seconde_action_donnee(modeladmin, request, queryset):
	pass
	
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

	# Permet d'afficher ce que renvoi le __str__ sur le panel admin
	list_display = ['__str__']
	list_per_page = 3

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
		fields = "__all__"

# Permet de gérer les formulaires (add et edit) // Encore à voir
class BookForm(forms.ModelForm):
	model = Book
	class Meta:
		# Affichage des champs dans la page d'ajout / edit
		fields = "__all__"
		
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Liste des champs que tu veux rendre non modifiables
		champs_ineditables = ['nb_selled_books', 'author']
		champs = list(self.fields.keys())
		
		disable_fields(self.fields, champs_ineditables)
		
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	# Champs affichés
	list_display = ['titre_colore', 'description', 'author', "nb_selled_books"]

	# Spécifie quelles actions sont liées à la page admin associée
	actions = [actiondonnee, seconde_action_donnee]

	def get_form(self, request, obj=None, **kwargs):
		if request.user.is_superuser:
			kwargs['form'] = AdminBookForm
		else:
			kwargs['form'] = BookForm		
		return super().get_form(request, obj, **kwargs)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):

	# Page perso html pour ajout / modification d'un elt
	change_form_template = "/home/loris/romain_porcer/django_tests/tutorial/project_test/apptestforadminpanel/templates/admin/apptestforadminpanel/adminPanelTest.html"


	filter_horizontal = ["linked_books"]

	# Sert à modifier tout des interfaces CRUD admin
	# Code de la doc  https://docs.djangoproject.com/fr/5.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.change_view

	def get_osm_info(self):
        # ...
		pass
	
	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra_context = extra_context or {}
		extra_context['osm_data'] = self.get_osm_info()
		return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )
	
#	class Media:  # Si on utilise du css, js, etc... dans la vue, le spécifier ici
#		css = {
#			"all": ["style_exemple.css"],
#		}
#		js = ["script_exemple.js"]

# A voir :
# radio_fields = {"group": admin.VERTICAL}  # Pour admin

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

	print(uneditable_fields)
	for	champ in uneditable_fields:
		if champ in form_fields_keys:
			form_fields[champ].disabled = True
##