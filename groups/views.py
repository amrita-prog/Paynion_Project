from django.shortcuts import render, redirect
from .forms import GroupCreateForm
from .models import Group

def create_group(request):
    if request.method == "POST":
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user  # auto set creator
            group.save()
            form.save_m2m()  # for saving members 

            return redirect("dashboard")
    else:
        form = GroupCreateForm()

    return render(request, "groups/create_group.html", {"form": form})


def delete_group(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect("dashboard")
    return render(request, "groups/confirm_delete.html", {"group": group})

def view_all_group(request):
    groups = Group.objects.all()
    return render(request, "groups/all_groups.html", {"groups": groups})
    