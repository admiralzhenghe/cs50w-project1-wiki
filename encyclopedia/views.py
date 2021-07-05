from django.shortcuts import render, redirect
from django.http import HttpResponse
from markdown2 import Markdown
from django import forms
from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    markdowner = Markdown()
    entry = util.get_entry(title)
    if entry == None:
        return render(request, "encyclopedia/missing.html", {
            "title": title
        })
    else:
        return render(request, "encyclopedia/found.html", {
            "converted": markdowner.convert(entry),
            "title": title
        })

def search(request):
    value = request.GET.get("q", "")
    result = util.get_entry(request.GET.get("q", ""))
    if result:
        return entry(request, value)
    elif result == None:
        match = []
        for item in util.list_entries():
            if value.upper() in item.upper():
                match.append(item)
        if len(match) == 0:
            return render(request, "encyclopedia/missing.html", { "title": value })
        else:
            return render(request, "encyclopedia/search.html", { "match": match })

class Form(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Title", "style": "margin-bottom: 10px; border-radius: 2.5px"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": "15", "cols": "75", "style": "margin-bottom: 10px; border-radius: 5px"}))

def new(request):
    entries = list(map(lambda x: x.upper(), util.list_entries()))
    if request.method == "POST":
        form = Form(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title.upper() in entries:
                return render(request, "encyclopedia/duplicate.html", {
                    "entry": Form(),
                })
            else:
                util.save_entry(title, content)
                return redirect(f"/wiki/{title}")
    else: #if request.method == "GET"
        return render(request, "encyclopedia/new.html", { "entry": Form() })

def edit(request, title):
    entry = util.get_entry(title)
    if request.method == "POST":
        entries = list(map(lambda x: x.upper(), util.list_entries()))
        new = Form(request.POST)
        if new.is_valid():
            original = title
            title = new.cleaned_data["title"]
            content = new.cleaned_data["content"]
            if not title.upper() in entries:
                return render(request, "encyclopedia/edit.html", {
                    "title": original,
                    "entry": Form(initial={'title': original, 'content': entry}),
                    "null": f"The entry {title} does not exist!"
                })
            else:
                util.save_entry(title, content)
                return redirect(f"/wiki/{title}")
    elif request.method == "GET":
        if entry:    
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "entry": Form(initial={'title': title, 'content': entry})
            })

def random(request):
    import random
    entries = util.list_entries()
    pick = random.randrange(0, len(entries))
    return redirect(f"/wiki/{entries[pick]}")