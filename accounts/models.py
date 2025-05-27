from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Gender(models.Model):
    """ジェンダーモデル"""

    type = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="性別"
    )

    def __str__(self):
        return self.type


class CustomUserManager(UserManager):
    """ユーザーマネージャー"""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email) # メールアドレスを正規化する（小文字統一）
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # パスワードをハッシュ化する
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True, unique=True)

    line_name = models.CharField(max_length=255, null=True, blank=True)
    line_id = models.CharField(max_length=255, null=True, blank=True)

    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    # ※　on_delete=models.SET_NULL  Gender削除時にnullにする
    #     null=True  デフォルト値が無くて良い
    #     blank=True  フォームでの入力を任意にする

    is_barrier_free = models.BooleanField(
        default=False,
        verbose_name="バリアフリー優先",
        help_text="このユーザーはバリアフリー優先かどうか"
    )

    # 管理サイトへのログインフラグ（True=管理者）
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )

    # アカウントフラグ（False=ログイン不可）
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    # User登録日
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
        # verbose_name="ユーザー登録日",
        help_text="ユーザーが登録された日時"
    )

    # User削除フラグ
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="削除フラグ",
        help_text="このユーザーが削除されたか"
    )

    # User削除日
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="削除日時",
        help_text="ユーザーが削除された日時"
    )

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        # 管理画面での表示名をuserに設定
        verbose_name = _('user')
        # 複数形の表示をusersに設定
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # def get_username(self):
    #     return self.username if self.username else self.email

    def __str__(self):
        return self.username if self.username else self.email