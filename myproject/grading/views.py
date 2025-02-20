from django.shortcuts import render, redirect
from .forms import CodeUploadForm, AnswerKeyForm
from .models import Submission, AnswerKey
from .utils import analyze_ast, check_syntax, clean_code, calculate_similarity
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, LoginForm
from .models import User

# View untuk Register
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Login otomatis setelah register
            return redirect('dashboard')  # Redirect ke dashboard
    else:
        form = RegisterForm()
    return render(request, 'grading/register.html', {'form': form})

# View untuk Login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Redirect setelah login
    else:
        form = LoginForm()
    return render(request, 'grading/login.html', {'form': form})

# View untuk Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# View untuk Redirect ke Dashboard berdasarkan Role
def dashboard_view(request):
    if request.user.is_authenticated:
        if request.user.role == "dosen":
            return render(request, 'grading/dosen_dashboard.html')
        elif request.user.role == "mahasiswa":
            return render(request, 'grading/mahasiswa_dashboard.html')
    return redirect('login')

def upload_code(request):
    ast_result = None
    syntax_feedback = None
    similarity_score = None
    latest_answer_key = AnswerKey.objects.last()  # Ambil kunci jawaban terbaru

    if request.method == "POST":
        if 'upload_answer_key' in request.POST:  # Jika dosen mengunggah kunci jawaban
            answer_form = AnswerKeyForm(request.POST, request.FILES)
            if answer_form.is_valid():
                answer_key = answer_form.save(commit=False)

                if request.FILES.get('uploaded_file'):  # Jika file diunggah
                    uploaded_file = request.FILES['uploaded_file']
                    answer_key.uploaded_code = uploaded_file.read().decode('utf-8')

                answer_key.save()
                return redirect('upload_code')

        elif 'upload_submission' in request.POST:  # Jika mahasiswa mengunggah jawaban
            form = CodeUploadForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)

                if request.FILES.get('uploaded_file'):  # Jika file diunggah
                    uploaded_file = request.FILES['uploaded_file']
                    submission.uploaded_code = uploaded_file.read().decode('utf-8')

                cleaned_code = clean_code(submission.uploaded_code)
                is_valid, syntax_feedback = check_syntax(cleaned_code, "StudentCode")

                if is_valid and latest_answer_key:
                    ast_result = analyze_ast(cleaned_code)
                    similarity_score = calculate_similarity(cleaned_code, latest_answer_key.uploaded_code)
                    submission.score = similarity_score
                else:
                    submission.score = 0

                submission.feedback = syntax_feedback
                submission.save()

                return render(request, 'grading/upload.html', {
                    'form': form,
                    'answer_form': answer_form,
                    'ast_result': ast_result,
                    'syntax_feedback': syntax_feedback,
                    'similarity_score': similarity_score,
                    'latest_answer_key': latest_answer_key
                })

    else:
        form = CodeUploadForm()
        answer_form = AnswerKeyForm()

    return render(request, 'grading/upload.html', {
        'form': form,
        'answer_form': answer_form,
        'latest_answer_key': latest_answer_key
    })

def home(request):
    return render(request, 'grading/home.html')