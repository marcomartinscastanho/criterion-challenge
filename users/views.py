import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from users.forms import ProfileForm


@login_required
def profile(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(request, "profile.html", {"form": form, "success": "Profile updated successfully!"})
        else:
            return render(request, "profile.html", {"form": form, "error": "The uploaded file must be a CSV file."})
    else:
        form = ProfileForm(instance=user)

    return render(request, "profile.html", {"form": form})


@login_required
def upload_csv(request: HttpRequest):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith(".csv"):
            return render(request, "upload_csv.html", {"error": "The uploaded file must be a CSV file."})
        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.reader(decoded_file)
            for row in reader:
                print(row)  # Replace with your processing logic
            return render(request, "upload_csv.html", {"success": "CSV file processed successfully!"})
        except Exception as e:
            return render(request, "upload_csv.html", {"error": f"An error occurred: {e}"})

    return render(request, "upload_csv.html")
