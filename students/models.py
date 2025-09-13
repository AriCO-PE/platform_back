import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ----------------
# USER MANAGER
# ----------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, role="student", first_name="", last_name="", **extra_fields):
        if not email:
            raise ValueError("El usuario debe tener un email")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            role=role,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)  # encripta contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, role="admin", **extra_fields)


# ----------------
# CUSTOM USER
# ----------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    # Nuevos campos
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    # Campos comunes
    birthday = models.DateField(null=True, blank=True)
    aura = models.IntegerField(default=0)
    specialty = models.CharField(max_length=200, blank=True, null=True)

    # Campos adicionales para profes
    experience_years = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Campos de control Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
