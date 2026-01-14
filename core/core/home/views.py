from django.shortcuts import render

from django.http import HttpResponse

def home(request):
    peoples = [
        {'name': 'sarvesh', "age": 20},
        {'name': 'arpit', "age": 21},
        {'name': 'sundram', "age": 15},
        {'name': 'saurabh', "age": 17},
        {'name': 'subhang', "age": 24},
    ]
    
    text = """
        loremorem ipsum dolor sit, amet consectetur adipisicing elit. Provident a aliquid eveniet inventore earum dolor molestiae consectetur possimus quibusdam sit aperiam architecto, quas saepe! Nostrum quam ab ullam saepe rem.
    """

    vegetables = ['cucumber', 'tomato', 'potato', 'greenchilli']

    return render(request, "home/index.html", context ={'page':'Dango tutorial', 'peoples': peoples, 'text': text, 'vegetables': vegetables})

def contact_page(request):
    context = {'page': 'Contact'}
    return render(request, "home/contact.html", context)

def about_page(request):
    context = {'page': 'About'}
    return render(request, "home/about.html", context)


def success_page(request):
    return HttpResponse("<h1>hey this is a Success page.</h1>")