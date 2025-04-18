from django.shortcuts import redirect
from .models import Review

# Create your views here.
def change_parent_type(req, queryset_ids):
	
    req.session['queryset_ids'] = queryset_ids
    return redirect('change_parent_type') 