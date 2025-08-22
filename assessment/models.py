from django.db import models
from django.conf import settings

class Subject(models.Model):
    exam_name = models.CharField(max_length=255)
    section_name = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()

    easy_question_count = models.PositiveIntegerField(default=0)
    medium_question_count = models.PositiveIntegerField(default=0)
    difficult_question_count = models.PositiveIntegerField(default=0)

    is_paid = models.BooleanField(default=True)

    marks_correct = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    marks_incorrect = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    marks_unattempted = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)  # When subject created
    updated_at = models.DateTimeField(auto_now=True)      # When subject updated

    def __str__(self):
        return f"{self.exam_name} - {self.section_name}"


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Difficult'),
    ]

    OPTION_CHOICES = [
        ('option_1', 'Option 1'),
        ('option_2', 'Option 2'),
        ('option_3', 'Option 3'),
        ('option_4', 'Option 4'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')

    question_text = models.TextField(blank=True, null=True)
    question_paragraph = models.TextField(blank=True, null=True)
    question_image = models.ImageField(upload_to='questions/', blank=True, null=True)

    option_1 = models.CharField(max_length=500)
    option_2 = models.CharField(max_length=500)
    option_3 = models.CharField(max_length=500)
    option_4 = models.CharField(max_length=500)

    correct_option = models.CharField(max_length=20, choices=OPTION_CHOICES)
    difficulty_level = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text[:50]

    def is_correct(self, selected_option: str) -> bool:
        """Check if a selected option matches the correct answer"""
        return selected_option == self.correct_option

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=255 , null=True)
    razorpay_payment_id = models.CharField(max_length=255 , null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
    


class AssessmentSession(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)

    overall_score = models.IntegerField(default=0)
    complete_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_test_end = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.id} - {self.user.username} ({self.status})"


class Attempt(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts')
    assessment_session = models.ForeignKey('AssessmentSession', on_delete=models.CASCADE, related_name='attempts')

    submit_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    start_time = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attempt {self.id} - {self.user.username} - {self.subject.exam_name}"



class AttemptAnswer(models.Model):
    OPTION_CHOICES = [
        ('option_1', 'Option 1'),
        ('option_2', 'Option 2'),
        ('option_3', 'Option 3'),
        ('option_4', 'Option 4'),
    ]
        
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_option = models.CharField(max_length=20, choices=OPTION_CHOICES)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(blank=True, null=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Answer for Q{self.question.id} in Attempt {self.attempt.id}"
