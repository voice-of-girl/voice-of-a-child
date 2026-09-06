"""Custom user model with platform-wide roles."""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must provide an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", CustomUser.Role.PLATFORM_ADMIN)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        PLATFORM_ADMIN = "PLATFORM_ADMIN", "Platform Admin"
        ORGANISATION_ADMIN = "ORGANISATION_ADMIN", "Organisation Admin"
        PROGRAMME_MANAGER = "PROGRAMME_MANAGER", "Programme Manager"
        MONITORING_OFFICER = "MONITORING_OFFICER", "Monitoring / Impact Officer"
        STAFF = "STAFF", "Staff / User"

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    role = models.CharField(
        max_length=30, choices=Role.choices, default=Role.STAFF
    )

    # Tenant binding. Null for platform admins; required for all other roles.
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_platform_admin(self):
        return self.role == self.Role.PLATFORM_ADMIN

    def organisations_visible(self):
        """
        Organisations this user may act upon.

        Platform admins see everything; everyone else only sees the
        organisation they belong to.
        """
        from apps.organisations.models import Organisation

        if self.is_platform_admin:
            return Organisation.objects.all()
        if self.organisation_id:
            return Organisation.objects.filter(id=self.organisation_id)
        return Organisation.objects.none()