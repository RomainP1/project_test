from django.db import models
from django.contrib import admin
from django.utils.html import format_html

# Create your models here.

# Simples models de test pour expérimenter gestion par panel admin


class Author(models.Model):
	name = models.CharField(max_length=50)
	surname = models.CharField(max_length=50)
	age = models.IntegerField(default=20)
	tel = models.CharField(max_length=10, default="0000000000")
	mail = models.EmailField(max_length=100, default="no@mails.gov", null=True)
	x = models.IntegerField(default=0)
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