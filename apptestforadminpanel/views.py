from django.shortcuts import render, HttpResponseRedirect
from .models import Review, Book

# Create your views here.
def change_parent_type(req):
    opts = Review._meta  # Assurez-vous que cela renvoie un objet avec un app_label valide
    reviews_id = req.GET['ids'].split(",") # Donne ce format : ['00001', '00002', '00003', ...]
    reviews_data = []
    parents = Book.objects.all()

    for id in reviews_id:
        reviews_data.append(Review.objects.get(pk=id))
    
    if req.method == "POST":
        
        # On récupère le type parent sélectionné en passant par l'id
        parent_to_link = Book.objects.get(pk=req.POST.get("selected-parent"))

        for review in reviews_data:
            review.reviewed_book = parent_to_link
            print(review.reviewed_book)
            review.save()
        return HttpResponseRedirect("/admin/apptestforadminpanel/review/")
    else :
       return render(req, 'admin/apptestforadminpanel/changeParentTypeForm.html', 
                  {'opts': opts, 'to_change_data':reviews_data, 'parents' : parents,
                   'form_title' : "Vous allez changer le livre associé à ces revues",
                   "reviews_id" : req.GET['ids']}) 