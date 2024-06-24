# import logging
# import json
# import os
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError
# from django.contrib.auth.password_validation import validate_password
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from django.conf import settings
# import yt_dlp as youtube_dl
# import assemblyai as aai
# import openai
# from openai.error import RateLimitError, InvalidRequestError

# # Setup logging
# logger = logging.getLogger(__name__)

# @login_required
# def index(request):
#     return render(request, 'index.html')

# @csrf_exempt
# def generate_blog(request):
#     if request.method != 'POST':
#         logger.error(f"Invalid request method: {request.method}")
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

#     try:
#         data = json.loads(request.body)
#         yt_link = data['link']
#         logger.info(f"Received YouTube link: {yt_link}")

#         # Download the audio from the YouTube video link
#         audio_file = download_audio(yt_link)
#         if not audio_file:
#             return JsonResponse({'error': 'Failed to download audio from YouTube'}, status=500)
#         logger.info(f"Downloaded audio file: {audio_file}")

#         # Get the transcript from the downloaded audio file
#         transcription = get_transcription(audio_file)
#         if not transcription:
#             return JsonResponse({'error': 'Failed to get transcript'}, status=500)
#         logger.info(f"Transcription: {transcription[:20]}...")  # Log only a snippet

#         # Generate blog content from the transcript using OpenAI
#         blog_content = generate_blog_from_transcription(transcription)
#         if not blog_content:
#             return JsonResponse({'error': 'Failed to generate blog article'}, status=500)
#         logger.info(f"Generated blog content length: {len(blog_content)} characters")

#         return JsonResponse({'content': blog_content})

#     except (KeyError, json.JSONDecodeError) as e:
#         logger.error(f"Invalid data sent: {e}")
#         return JsonResponse({'error': 'Invalid data sent'}, status=400)
#     except RateLimitError as e:
#         logger.error(f"Rate limit exceeded: {e}")
#         return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
#     except InvalidRequestError as e:
#         logger.error(f"Invalid request: {e}")
#         return JsonResponse({'error': 'Invalid request. Please check your input and try again.'}, status=400)
#     except Exception as e:
#         logger.error(f"Error generating blog article: {e}", exc_info=True)
#         return JsonResponse({'error': f'Error generating blog article: {str(e)}'}, status=500)

# def download_audio(link):
#     try:
#         ydl_opts = {
#             'format': 'bestaudio/best',
#             'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(id)s.%(ext)s'),
#             'postprocessors': [{
#                 'key': 'FFmpegExtractAudio',
#                 'preferredcodec': 'mp3',
#                 'preferredquality': '192',
#             }],
#             'ffmpeg_location': 'C:\\ffmpeg\\bin',  # Ensure this is the correct path
#         }
#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(link, download=True)
#             audio_file = os.path.join(settings.MEDIA_ROOT, f"{info_dict['id']}.mp3")
#         return audio_file
#     except Exception as e:
#         logger.error(f"Error downloading audio with yt-dlp: {e}", exc_info=True)
#         return None

# def get_transcription(audio_file):
#     try:
#         logger.info(f"Starting transcription for audio file: {audio_file}")
#         aai.settings.api_key = "2eb78d816dd34b9db88e489d92a1def8"
#         transcriber = aai.Transcriber()  # Correctly instantiate the transcriber
#         transcript = transcriber.transcribe(audio_file)
#         logger.info(f"Transcription complete. Transcript length: {len(transcript.text)} characters")
#         return transcript.text
#     except Exception as e:
#         logger.error(f"Error getting transcription: {e}", exc_info=True)
#         return None

# def generate_blog_from_transcription(transcription):
#     try:
#         logger.info("Starting blog generation from transcription")
#         openai.api_key = "sk-proj-etkWnVbzxXtbjFTE2nANT3BlbkFJD2mFew0loEAkYnBjp81I"
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": f"Based on the following transcript from a YouTube video, write a comprehensive blog article. Make it look like a proper blog article:\n\n{transcription}\n\nArticle:"}
#         ]

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             max_tokens=1000
#         )
#         generated_content = response.choices[0].message['content'].strip()
#         logger.info(f"Blog generation complete. Content length: {len(generated_content)} characters")
#         return generated_content
#     except RateLimitError as e:
#         logger.error(f"Rate limit exceeded: {e}")
#         return None
#     except InvalidRequestError as e:
#         logger.error(f"Invalid request: {e}")
#         return None
#     except Exception as e:
#         logger.error(f"Error generating blog content: {e}", exc_info=True)
#         return None

# def user_signup(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         cpassword = request.POST.get('cpassword')

#         if not all([username, email, password, cpassword]):
#             error_message = 'All fields are required'
#             return render(request, 'signup.html', {'error_message': error_message})

#         if password != cpassword:
#             error_message = 'Passwords do not match'
#             return render(request, 'signup.html', {'error_message': error_message})

#         try:
#             validate_password(password)
#         except ValidationError as e:
#             return render(request, 'signup.html', {'error_message': e.messages})

#         try:
#             if User.objects.filter(username=username).exists():
#                 error_message = 'Username already taken'
#                 return render(request, 'signup.html', {'error_message': error_message})

#             if User.objects.filter(email=email).exists():
#                 error_message = 'Email already registered'
#                 return render(request, 'signup.html', {'error_message': error_message})

#             user = User.objects.create_user(username, email, password)
#             user.save()
#             login(request, user)
#             return redirect('index')  # Assuming 'index' is the name of your home page URL pattern
#         except Exception as e:
#             error_message = f'Error creating account: {str(e)}'
#             return render(request, 'signup.html', {'error_message': error_message})

#     return render(request, 'signup.html')

# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         if not username or not password:
#             error_message = 'Both username and password are required'
#             return render(request, 'login.html', {'error_message': error_message})

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('index')  # Assuming 'index' is the name of your home page URL pattern
#         else:
#             error_message = "Invalid username or password"
#             return render(request, 'login.html', {'error_message': error_message})

#     return render(request, 'login.html')

# def user_logout(request):
#     logout(request)
#     messages.success(request, "Logged out successfully!")
#     return redirect('login')  #  'login' is the name of login page URL pattern


from transformers import pipeline
import logging
import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import yt_dlp as youtube_dl
import assemblyai as aai

# Setup logging
logger = logging.getLogger(__name__)

@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method != 'POST':
        logger.error(f"Invalid request method: {request.method}")
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        yt_link = data['link']
        logger.info(f"Received YouTube link: {yt_link}")

        # Download the audio from the YouTube video link
        audio_file = download_audio(yt_link)
        if not audio_file:
            return JsonResponse({'error': 'Failed to download audio from YouTube'}, status=500)
        logger.info(f"Downloaded audio file: {audio_file}")

        # Get the transcript from the downloaded audio file
        transcription = get_transcription(audio_file)
        if not transcription:
            return JsonResponse({'error': 'Failed to get transcript'}, status=500)
        logger.info(f"Transcription: {transcription[:100]}...")  # Log only a snippet

        # Generate blog content from the transcript using GPT-2
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': 'Failed to generate blog article'}, status=500)
        logger.info(f"Generated blog content length: {len(blog_content)} characters")

        return JsonResponse({'content': blog_content})

    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Invalid data sent: {e}")
        return JsonResponse({'error': 'Invalid data sent'}, status=400)
    except Exception as e:
        logger.error(f"Error generating blog article: {e}", exc_info=True)
        return JsonResponse({'error': f'Error generating blog article: {str(e)}'}, status=500)

def download_audio(link):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': 'C:\\ffmpeg\\bin',  # Ensure this is the correct path
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = os.path.join(settings.MEDIA_ROOT, f"{info_dict['id']}.mp3")
        return audio_file
    except Exception as e:
        logger.error(f"Error downloading audio with yt-dlp: {e}", exc_info=True)
        return None

def get_transcription(audio_file):
    try:
        logger.info(f"Starting transcription for audio file: {audio_file}")
        aai.settings.api_key = "YOUR_ASSEMBLYAI_API_KEY"  # Replace with your actual API key
        transcriber = aai.Transcriber()  # Correctly instantiate the transcriber
        transcript = transcriber.transcribe(audio_file)
        logger.info(f"Transcription complete. Transcript length: {len(transcript.text)} characters")
        return transcript.text
    except Exception as e:
        logger.error(f"Error getting transcription: {e}", exc_info=True)
        return None

def generate_blog_from_transcription(transcription):
    try:
        logger.info("Starting blog generation from transcription using GPT-2")

        # Initialize the text generation pipeline
        generator = pipeline('text-generation', model='gpt2', max_length=500)

        # Generate the blog content
        prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article:\n\n{transcription}\n\nArticle:"
        results = generator(prompt, max_length=1000, num_return_sequences=1)

        generated_content = results[0]['generated_text']
        logger.info(f"Blog generation complete. Content length: {len(generated_content)} characters")
        return generated_content.strip()
    
    except Exception as e:
        logger.error(f"Error generating blog content with GPT-2: {e}", exc_info=True)
        return None

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if not all([username, email, password, cpassword]):
            error_message = 'All fields are required'
            return render(request, 'signup.html', {'error_message': error_message})

        if password != cpassword:
            error_message = 'Passwords do not match'
            return render(request, 'signup.html', {'error_message': error_message})

        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, 'signup.html', {'error_message': e.messages})

        try:
            if User.objects.filter(username=username).exists():
                error_message = 'Username already taken'
                return render(request, 'signup.html', {'error_message': error_message})

            if User.objects.filter(email=email).exists():
                error_message = 'Email already registered'
                return render(request, 'signup.html', {'error_message': error_message})

            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return redirect('index')  # Assuming 'index' is the name of your home page URL pattern
        except Exception as e:
            error_message = f'Error creating account: {str(e)}'
            return render(request, 'signup.html', {'error_message': error_message})

    return render(request, 'signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            error_message = 'Both username and password are required'
            return render(request, 'login.html', {'error_message': error_message})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Assuming 'index' is the name of your home page URL pattern
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')  
