from django.db import models
from django.conf import settings

from django.core.validators import FileExtensionValidator


class Environment(models.Model):
  code     = models.CharField(max_length=10, unique=True)
  name     = models.CharField(max_length=100)
  order    = models.PositiveIntegerField(default = 0)
  approval_required = models.BooleanField(default=False)
  
  class Meta:
    ordering = ["order"]
    db_table = "Environment"
  
  def __str__(self):
    return self.code


class DatabaseTarget(models.Model):
  name        = models.CharField(max_length=100)
  sgbd        = models.CharField(max_length=20)
  dsn         = models.CharField(max_length=100)
  secret_path = models.CharField(max_length=100)
  active      = models.BooleanField(default=True),
  
  environment = models.ForeignKey(Environment, on_delete=models.PROTECT, related_name="database")
  
  class Meta:
    db_table = "DatabaseTarget"
  
  def __str__(self):
    return self.name


class Release(models.Model):
  title = models.CharField(max_length=100)
  description = models.TextField(max_length=500, null=True)
  
  approved_at  = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
  scheduled_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
  create_at    = models.DateTimeField(auto_now=True , auto_now_add=True),
  update_at    = models.DateTimeField(auto_now=False, auto_now_add=False, null=True),
  
  author   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="authored_releases")
  approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approved_releases", null=True)

  target = models.ForeignKey(DatabaseTarget, on_delete=models.PROTECT, related_name="releases")

  class Status(models.TextChoices):
    DRAFT     = "DRAFT"    , "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    APPROVED  = "APPROVED" , "Approved"
    REJECTED  = "REJECTED" , "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"
    
  status = models.CharField(
    max_length = 20,
    choices    = Status.choices,
    default    = Status.DRAFT,
    db_index   = True,
  )

  class Meta:
    db_table = "Release"
    permissions = [
      ("approve_release", "Can approve a release"),
      ("submit_release", "Can submit a release for approval"),
      ("execute_release", "Can execute or schedule a release"),
    ]

  def __str__(self):
    return self.title


class Script(models.Model):
  name          = models.CharField(max_length=100),
  order         = models.IntegerField(default=0),
  
  file          = models.FileField(upload_to="script/%Y/%m/"  , validators=[FileExtensionValidator(allowed_extensions="sql")])
  rollback_file = models.FileField(upload_to="rollback/%Y/%m/", validators=[FileExtensionValidator(allowed_extensions="sql")], null=True) 
  
  content_hash  = models.CharField(max_length=64, editable=False, null=True)
  
  release = models.ForeignKey(Release, on_delete=models.PROTECT, related_name="scripts")

  class Meta:
    db_table = "Script"

  def __str__(self):
    return self.name