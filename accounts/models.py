from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, is_active, first_name, last_name, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not is_active:
            raise ValueError("User must have an active status")
        if not first_name:
            raise ValueError("User must have an first name")
        if not last_name:
            raise ValueError("User must have an last name")

        user_obj = self.model(
            email=self.normalize_email(email),
            is_active=is_active,
            first_name=first_name,
            last_name=last_name)

        user_obj.set_password(password)
        user_obj.save(using=self._db)

        return user_obj

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            is_active=True,
            first_name=first_name,
            last_name=last_name,
            password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    # first_name = models.CharField(verbose_name='first name', max_length=20, null=True)
    full_name = models.CharField(verbose_name='full name', max_length=30, null=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_signup = models.BooleanField(default=True)
    # role = models.CharField(max_length=1, default='U', choices=[('U','User'), ('A', 'Admin')])

    objects = UserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        return super(self.__class__, self).save(*args, **kwargs)

    # @property
    # def get_name(self):
    #     return f'{self.first_name} {self.last_name}'


class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)
    classification = models.CharField(max_length=50)
    confidence = models.CharField(max_length=10)
    description = models.TextField()
    solution = models.TextField()


class ContactUs(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=60)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)