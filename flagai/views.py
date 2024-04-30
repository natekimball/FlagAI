import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from flagai.models import File, Report
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
import boto3
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from django.core.mail import send_mail

import os
from dotenv import load_dotenv
load_dotenv()

@login_required

def index(request):
    if request.user.email in ["flagai.manager@gmail.com", "cs3240.super@gmail.com"]:
        group, created = Group.objects.get_or_create(name='site_admin')
        request.user.groups.add(group)

    is_user_admin = request.user.groups.filter(name='site_admin').exists()
    is_user_anonymous = request.user.groups.filter(name='anonymous').exists()

    s3_base_url = f'{os.getenv("AWS_S3_ENDPOINT_URL")}{os.getenv("AWS_STORAGE_BUCKET_NAME")}'

    # Define the custom order for the report status
    status_ordering = Case(
        When(status='New', then=Value(1)),
        When(status='In Progress', then=Value(2)),
        When(status='Resolved', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )

    if is_user_admin:
        # Annotate and order the reports based on the custom order
        reports = Report.objects.annotate(
            custom_order=status_ordering
        ).order_by('custom_order', '-date_uploaded_or_edited')
        return render(request, 'flagai/admin_index.html', {
            'reports': reports,
            's3_base_url': s3_base_url  # Assuming you want to use this in the admin index as well
        })
    elif is_user_anonymous:
        return redirect('reports/create')
    else:
        user_reports = Report.objects.filter(user=request.user).annotate(
            custom_order=status_ordering
        ).order_by('custom_order', '-date_uploaded_or_edited')
        return render(request, 'flagai/common_index.html', {
            'user_reports': user_reports,
            'is_user_anonymous': is_user_anonymous,
            's3_base_url': s3_base_url
        })
def profile(request):
    is_user_admin = request.user.groups.filter(name='site_admin').exists()
    is_user_anonymous = request.user.groups.filter(name='anonymous').exists()
    return render(request, 'flagai/profile.html', {'is_user_admin': is_user_admin, 'is_user_anonymous': is_user_anonymous})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('flagai:index')
    return render(request, "flagai/login.html")


def logout_view(request):
    logout(request)
    return redirect("/")

def about(request):
    return render(request, 'flagai/about.html')


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "admin":
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                auth_login(request, user)
                return redirect('/admin/')
            else:
                messages.error(request, 'Invalid credentials or you are not an admin.')
        else:
            messages.error(request, 'Only the admin can access this area.')

    return render(request, 'flagai/login.html', {'messages': messages.get_messages(request)})

@require_POST
@login_required
def update_report_status(request, report_id):
    new_status = request.POST.get('new_status', '')
    feedback = request.POST.get('feedback', '')  # Get feedback from POST data, default to empty string

    try:
        report = Report.objects.get(id=report_id)
        if new_status:
            report.status = new_status
        if feedback:
            report.feedback = feedback
        report.save()

        subject = f"FlagAI Report has new updates"
        message = f"Your FlagAI report has been updated by a site admin. Please check back into the site to view these changes.\n The report description is {report.description}."
        send(report, subject, message)

        return JsonResponse({'success': True, 'new_status': report.status, 'feedback': report.feedback})
    except Report.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def anonymous_login(request):
    username = "anonymous"
    password = ".2nq6E$2H.@s_cu"
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect('/')

    return render(request, 'flagai/login.html', {'messages': messages.get_messages(request)})

def create_report(request):
    if request.method == 'POST':
        description = request.POST.get('description')

        offender_link = request.POST.get('offender_link')

        people_involved = request.POST.get('people_involved')

        contact_email = request.POST.get('contact_email') or ''

        user = request.user if request.user.is_authenticated else None

        report = Report(
            user=user,
            description=description,
            offender_link=offender_link,
            people_involved=people_involved,
            contact_email=contact_email,
            feedback="",
            date_uploaded_or_edited=now(),
            status='New'
        )
        report.save()
        files = request.FILES.getlist('file_uploads')
        for file_field in files:
            original_filename = file_field.name
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''

            file_field.name = f"{original_filename.split('.')[0] if '.' in original_filename else ''}_{uuid.uuid4()}.{file_extension}"
            file_instance = File(file=file_field, name=original_filename, report=report)
            file_instance.save()

        messages.success(request, 'Report created successfully!')

        subject = f"FlagAI Report submitted successfully"
        message = f"Your FlagAI report was submitted successfully. Your submission is now pending review."
        send(report, subject, message)

        return redirect('flagai:index')
    else:
        return render(request, 'flagai/create_report.html')


def download_file_from_s3(request, file_id):
    file_instance = File.objects.get(id=file_id)  # objects is not an error
    file_link = f'{os.getenv("AWS_S3_ENDPOINT_URL")}{os.getenv("AWS_STORAGE_BUCKET_NAME")}/{file_instance.file}'
    return redirect(file_link)


def delete_report(request, report_id):
    report = Report.objects.get(id=report_id)
    files = report.files.all()
    for file in files:
        file.delete()
    report.delete()
    return redirect("/")

def send(report, subject, message):
    # if it is not an anonymous user, use a better way to do this check bc doesn't work is someones name in gmail is anonymous
    if report.user.username != "anonymous":
        send_mail(subject, message, 'flagai.a13@gmail.com', [report.user.email, ], auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD)
