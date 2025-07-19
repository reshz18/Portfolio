from django.shortcuts import render
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm
from .models import ContactMessage
import json

def home(request):
    return render(request, 'main/index.html')

@csrf_exempt  # Remove in production and use proper CSRF handling
def contact_form(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            form = ContactForm(data)
            
            if form.is_valid():
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']

                # Save to database
                ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )

                # Format email content
                email_subject = f"New Contact Form Submission: {subject}"
                email_body = f"""
                Name: {name}
                Email: {email}
                Subject: {subject}
                
                Message:
                {message}
                
                ---
                Sent from your portfolio website
                """.strip()

                # Send email
                send_mail(
                    email_subject,
                    email_body,
                    settings.EMAIL_HOST_USER,  # From email (uses settings.py)
                    [settings.EMAIL_HOST_USER],  # To email
                    fail_silently=False,
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Your message has been sent successfully!'
                })
            else:
                # Return form validation errors
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors,
                    'message': 'Please correct the errors below.'
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)