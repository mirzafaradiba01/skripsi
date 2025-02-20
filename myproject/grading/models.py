from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('dosen', 'Dosen'),
        ('mahasiswa', 'Mahasiswa'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='mahasiswa')

    def __str__(self):
        return f"{self.username} ({self.role})"


class AnswerKey(models.Model):  # Kunci jawaban (diunggah oleh dosen)
    uploaded_code = models.TextField(blank=True, null=True)  # Kunci jawaban dalam bentuk teks
    uploaded_file = models.FileField(upload_to='answer_keys/', blank=True, null=True)  # Kunci jawaban dalam bentuk file
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Waktu upload terakhir

    def __str__(self):
        return f"Kunci Jawaban - {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"

class Submission(models.Model):  # Jawaban mahasiswa
    student_name = models.CharField(max_length=100)
    uploaded_code = models.TextField(blank=True, null=True)  # Jawaban dalam bentuk teks
    uploaded_file = models.FileField(upload_to='uploads/', blank=True, null=True)  # Jawaban dalam bentuk file
    score = models.FloatField(null=True, blank=True)  # Skor similarity
    feedback = models.TextField(null=True, blank=True)  # Hasil pengecekan sintaks
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - Score: {self.score}"
