import json
import os
from django.db import models
from django.contrib import admin
from django.core.validators import RegexValidator, DecimalValidator
from django.utils.html import format_html
import re
import pickle
from typing import List
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as gt
# Create your models here.

# # # DP Observer (useful for validators) 
class Observer:
	data = {}

	def update_data(data_key, data_value):
		pass # To implement in child class

class Subject:

	def __init__(self):
		# We specify that only observers are allowed
		self.observers = []

	def add_observer(self, observer : Observer):
		self.observers.append(observer)	


	def remove_observer(self, observer : Observer):
		if (observer in self.observers):
			self.observers.remove(observer)	
			return True
		return False
	
	def update_observers(self, received_data: dict):
		for observer in self.observers:
			for key, val in received_data.items():
				observer.update_data(key, val)
			

# # # Singleton

class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


# # # Validateurs / Contraintes pour saisi de champs

def too_long_word_validator(input):
	if (len(input) > 50):
		raise ValidationError( # Format conseillé pour les validationErrors
            gt("%(value)s est trop long !"),
            params={"value": input},
        )

def too_small_word_validator(input):
	if (len(input) < 3):
		raise ValidationError(
            gt("%(value)s est trop court !"),
            params={"value": input},
        )

def mail_validator(val):
	if (not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', val)):
		raise ValidationError(
            gt("%(value)s n'est pas un mail valide !"),
            params={"value": val},
        )

def superior_to_limit(val):
	donnee_lim = ValidatorData().get_data()
	print(donnee_lim)
	if (val > int(donnee_lim["limite_donnee_a"])):
		raise ValidationError(
            gt("%(value)s est superieur à la donnée limite a, qui est %(donnee_lim)s !"),
            params={"value": val, "donnee_lim" : donnee_lim["limite_donnee_a"]},
        )


def num_chassis_validator(saisie):	
	if (not re.match(r"[A-HJ-NPR-Z0-9]{17}", saisie)):
		raise ValidationError(
            gt("%(value)s n'est pas un chassis valide !"),
            params={"value": saisie},
        )

def date_futur_validator(date):
	today = datetime.datetime.now()

	if (date < today.date()):
		raise ValidationError(
            gt("La date dois être supérieur ou égale à la date courante !"),
        )

def password_validator(password):
	password_errors = []
	if (len(password) < 10):
		password_errors.append(
			ValidationError(gt("Ce champ faire au minimum 10 caractères"), 
							code="too_short_password"))
	
	if (not re.match("^.*[%+_/#]+.*$", password)):
		password_errors.append(
			ValidationError(gt("Ce champ doit contenir au moins 1 caractère spécial (%, +, _, /, #)"),
							code="no_special_chars_password"))
	
	if (not re.match("^.*[0-9]+.*$", password)):
		password_errors.append(
			ValidationError(gt("Ce champ doit contenir au moins 1 chiffre"),
							code="no_special_chars_password"))

	if (password.islower()):
		password_errors.append(
			ValidationError(gt("Ce champ doit contenir au moins 1 majuscule"),
							code="no_special_chars_password"))

	if (len(password_errors) > 0):
		raise ValidationError(password_errors)
		

def val_debut_plus_grand_fin(start_value, end_value):
	# TODO : Vérifier le type d'objet pour faire la vérif
	return start_value > end_value

def donnee_a_unique_validator(self):
	""" Description
	:type self: Model
	:param self: Model détenant des valeurs à vérifier comme unique

	:rtype: tuple (boolean, Model,)
	:returns: faux ssi au moins une autre occurence est trouvé, 
			  avec la référence de l'objet de la première occurence trouvée.
			  Sinon, renvoi vrai et None 
	"""
	est_unique = True
	ref_redondante = None
	for obj in testToValidateData.objects.all():
		if (obj.donnee_a_unique == self.donnee_a_unique and obj != self):
			est_unique = False
			ref_redondante = obj

	return (est_unique, ref_redondante,)

# Simples models de test pour expérimenter gestion par panel admin


class Author(models.Model):
	name = models.CharField(max_length=50)
	surname = models.CharField(max_length=50)
	age = models.IntegerField(default=20)
	tel = models.CharField(max_length=10, default="0000000000")
	mail = models.CharField(max_length=100, default="no@mails.gov", null=True, validators=[mail_validator])
	x = models.IntegerField(default=0, validators=[superior_to_limit,])
	xTimesTwo = models.IntegerField(default=0)

	

	def __str__(self):
		return f"{self.name.upper()} {self.surname}"


class Book(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.CharField(max_length=121, null=False)
	description = models.CharField(max_length=300)
	nb_selled_books = models.IntegerField(default=0)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)


	def __str__(self):
		return  self.title
	
	# Permet de gérer l'affichage de chaque élément d'une colonne (ici title)
	@admin.display(ordering="title")
	def titre_colore(self):
	    return format_html(
            '<span style="color:rgb(92, 74, 63); font-size: 20px; font-style:italic">{}</span>',
            self.title,)


class Genre(models.Model):
	name = models.CharField(max_length=100)
	linked_books = models.ManyToManyField(Book, through="RelationbookGenre")

	def __str__(self):
		return self.name

class Review(models.Model):
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=400)
	overall_note = models.IntegerField()
	reviewed_book = models.ForeignKey(Book, on_delete=models.CASCADE)

	
class RelationBookGenre(models.Model):
	book = models.ForeignKey(Book, on_delete=models.CASCADE)
	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
	note = models.TextField(max_length=200, default="")

	def __str__(self):
		return self.book.title
		
class testToValidateData(models.Model, Subject):
	id = models.AutoField(primary_key=True)
	num_tel = models.IntegerField(null=True)
	num_chassis = models.CharField(max_length=300, 
								  validators=[too_long_word_validator, too_small_word_validator,
											  RegexValidator( # Valide par un regex
												regex=r"[A-HJ-NPR-Z0-9]{17}",
												message=  "Entrez un chassis valide "
						 								+ "(Pas de O, I ou de Q)"
						 								+ " -- Ce champ doit faire 17 caractères"
														+ ", et être exclusivement composé de chiffes"
														+ " et de lettres en majuscules", # ! TODO Ne gère pas les majuscules
												code="chassis_invalide")])
	date_debut = models.DateField(validators=[date_futur_validator,])
	date_fin = models.DateField()
	heure_debut = models.TimeField()
	heure_fin = models.TimeField()
	date_heure_debut = models.DateTimeField()
	date_heure_fin = models.DateTimeField()
	password = models.CharField(max_length=200, validators=[password_validator])
	donnee_a_unique = models.CharField(max_length=200)
	limite_donnee_a = models.CharField(max_length=200) 
	donnee_logique_complexe_a = models.CharField(max_length=300)
	donnee_logique_complexe_b = models.CharField(max_length=300)
	donnee_logique_complexe_c = models.CharField(max_length=300)
	nb_a_virgule = models.DecimalField(decimal_places=2, max_digits=5)

	# # # Interaction avec l'observateur
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_observer(ValidatorData())

	# Méthode exécutée pour faire la validation des données. 
	# Exécute to_python(), validate() et run_validator() avant
	# d'exécuter le code donné sous le super().clean() 
	def clean(self):
		cleaned_data = super().clean()

		errors = []

		if (val_debut_plus_grand_fin(self.date_debut, self.date_fin)):
			# * Si on a un problème avec les dates
			errors.append(
				ValidationError(
					gt("La date de début doit être antérieure à celle de fin !"), 
					code="dates_order"))
			# TODO : Afficher l'erreur à l'emplacement du field admin	

		if (val_debut_plus_grand_fin(self.heure_debut, self.heure_fin)):
			# * Si on a un problème avec les heures
			errors.append(
				ValidationError(
					gt("L'heure de début doit être antérieure à celle de fin !"), 
					code="hours_order"))
			# TODO : Afficher l'erreur à l'emplacement du field admin

		is_unique, ref_redondante = donnee_a_unique_validator(self)
		if (not is_unique):
			# * Si on a un problème avec les données a demandées unique
			errors.append(			
				ValidationError(
					gt('La donnée "%(donnee)s" doit être unique ! Redondance avec %(autre_obj)s'),
					params={'autre_obj': ref_redondante.__str__(),
							'donnee': self.donnee_a_unique},
			))
		

		if (len(errors) > 0): # Des erreurs sont à corriger
			raise ValidationError(errors)
		else : # On envoi les données voulues à l'observateur et le form est validé 
			self.update_observers({"limite_donnee_a": self.limite_donnee_a})


	def __str__(self):
		return f"{self.id} -- {self.num_chassis}"
	


class ValidatorData(Singleton, Observer):
	"""
	Serve to centralize data for validating forms

	Is set as an observer to update itself when a data is changed in a form
	"""

	# Loading data from a file
	_data = {}
	if (os.path.isfile("./validator_data.txt")):
		with open("./validator_data.txt","r") as file:
			file_content = file.read()
			_data = json.loads(file_content)

	# Allows to generate Singleton
	def __new__(class_, *args, **kwargs): 
		return super().__new__(ValidatorData, *args, **kwargs)

	def update_data(self, data_key, data_value):
		""" Description : Allows to update data from different validation constrains
		
			:type data_key: Object
			:param data_key: the referenced key for the validator constraint
		
			:type data_value: Object
			:param data_value: the current constraint
		"""
		self._data.update({data_key : data_value})

		# Save the constraint in a file
		json_data = json.dumps(self._data)
		with open("./validator_data.txt","w") as file:
			file.write(json_data)
	 
	def get_data(self):
		return self._data
