from django.db import models
from django.conf import settings 
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from constants.student_profiles import *

class StudentProfile(models.Model):   
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField( 
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,  
    )   
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=100) 
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)  
    city = models.CharField(max_length=100)  
    state = models.CharField(max_length=100)  
    postal_code = models.IntegerField(validators=[MaxValueValidator(999999)])  
    country = models.CharField(max_length=100)  
    experience = models.PositiveSmallIntegerField(validators=[MaxValueValidator(99)])  
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2)
    expecting_salary = models.DecimalField(max_digits=10, decimal_places=2)
    job_search_status = models.PositiveSmallIntegerField(choices=SEARCH_STATUS_CHOICES) 
    interests = models.TextField(blank=True, null=True, max_length=400)
    notice_period = models.PositiveSmallIntegerField(choices=NOTICE_PERIOD_CHOICES)  
    short_bio = models.TextField(max_length=400)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.designation}"



class AcademicQualification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey( 
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
    )
    institution_name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100)  
    start_year = models.DateField()
    end_year = models.DateField()
    
    def __str__(self):
        return f"{self.institution_name} - {self.specialization}"

    
class WorkExperience(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    organization_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=100)
    start_date = models.DateField()  
    end_date = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.organization_name} - {self.designation}"


class SkillSet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=50)  
    experience = models.PositiveIntegerField()  
    
    def __str__(self):
        return f"{self.user} - {self.skill_name}"

    
class Certifications(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    certification_name = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)  
    end_date = models.DateField(null=True, blank=True) 
    certificate_url = models.URLField(blank=True, null=True)  
    
    def __str__(self):
        return f"{self.certification_name}"

    
class Projects(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    project_name = models.CharField(max_length=200)
    description = models.TextField(max_length=500, blank=True, null=True)
    project_url = models.URLField(blank=True, null=True)  
    
    def __str__(self):
        return f"{self.project_name} - {self.user}"


class SocialUrls(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    link = models.URLField(blank=True)  
    link_title = models.CharField(blank=True, null=True)  
    
    def __str__(self):
        return f"{self.link} - {self.link_title}"