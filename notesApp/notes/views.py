from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from notes.models import *
import os
# Create your views here.
def home(request):
    return render(request, 'home.html')

def add_note(request):

    if request.method == "POST":
        Note.objects.create(
            title = request.POST.get('title'),
            description = request.POST.get('description'),  
            file = request.FILES.get('file'),
        )
        return redirect('view_notes')



    return render(request, "add.html")

def view_notes(request):

    notes = Note.objects.all().order_by('-created_at')
    
    context = {'notes': notes}
    return render(request, "view.html", context)



def delete_note(request, id):

    note = get_object_or_404(Note, id=id)
    note.delete()
    return redirect('view_notes')



def download_file(request, id):
    note = get_object_or_404(Note, id=id)
    return FileResponse(
        note.file.open('rb'),
        as_attachment=True,
        filename=os.path.basename(note.file.name)
    )