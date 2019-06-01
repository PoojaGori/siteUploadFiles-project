from django.db import models

from django.utils import timezone

# Create your models here.

class SubmissionDetails(models.Model):

    submissionCode = models.CharField(max_length=100, blank=True, null =True)
    process_department = models.CharField(max_length=20)
    file_path = models.CharField(max_length=50)
    uploaded_file_name = models.CharField(max_length=50,blank=True, null=True)

    file_size = models.CharField(max_length=20,blank=True, null=True)
    process_ent_id = models.CharField(max_length=20)
    submitted_by = models.CharField(max_length=20, editable=False)
    project = models.CharField(max_length=50, editable=False)
    project_code = models.CharField(max_length=20,blank=True, null=True, editable=False)
    asset = models.CharField(max_length=30, editable=False)
    asset_code = models.CharField(max_length=20,blank=True, null=True, editable=False)
    version = models.CharField(max_length=30, editable=False)
    submission_date = models.DateTimeField(default=timezone.now,editable=False)
    comments = models.TextField(max_length=50,blank=True, null=True)

    readable_file_size = models.CharField(max_length=20,blank=True, null=True)
    python_chunk_size = models.CharField(max_length=20,blank=True, null=True)
    ftplib_chunk_size = models.CharField(max_length=20,blank=True, null=True)
    time_to_upload_in_seconds = models.CharField(max_length=20,blank=True, null=True)
    time_to_upload_in_hms = models.CharField(max_length=20,blank=True, null=True)
    final_upload_status = models.CharField(max_length=20,blank=True, null=True)
    logs = models.TextField(max_length=100,blank=True, null=True)

    test_average_upload_speed = models.CharField(max_length=20,blank=True, null=True)
    test_ftp_upload_time = models.CharField(max_length=20,blank=True, null=True)
