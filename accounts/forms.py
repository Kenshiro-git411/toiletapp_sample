from django import forms
from .models import Gender, User
from django.contrib.auth.password_validation import validate_password
from datetime import datetime
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

# 仮想環境の修正は行わず、継承する
class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["class"] = "w-full p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"

# 仮想環境の修正は行わず、継承する
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].widget.attrs["class"] = "p-1 ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"
        self.fields["new_password2"].widget.attrs["class"] = "p-1 ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="メールアドレス",
        widget=forms.TextInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"})
    )
    password = forms.CharField(
        label="パスワード",
        widget=forms.PasswordInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"})
    )

class SigninForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label="パスワード再入力",
        widget=forms.PasswordInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"})
    )
    gender = forms.ModelChoiceField(
        queryset=Gender.objects.all(), # DBデータの取得
        widget=forms.Select(attrs={"class": "ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"}),
        empty_label="選択してください",
        label="性別"
    )
    is_barrier_free = forms.BooleanField(
        required=False,
        label="バリアフリー優先",
    )

    class Meta:
        model = User
        fields=["email", "password", "username"]
        labels={
            "email": "メールアドレス",
            "password": "パスワード",
            "username": "ユーザー名",
        }
        widgets = {
            "email": forms.EmailInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"}),
            "password": forms.PasswordInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"}),
            "username": forms.TextInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"}),
        }

    def clean_email(self):
        """メールアドレスのバリデーション"""
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        # print("email", email)
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("このメールアドレスは既に使用されています")
        return email

    def clean_username(self):
        """ユーザー名のバリデーション"""
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        if not username:
            raise forms.ValidationError("ユーザー名を入力してください")
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("このユーザー名は既に使用されています")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        # print('password', password)
        confirm_password = cleaned_data.get("confirm_password")
        # print(confirm_password)
        if password != confirm_password:
            raise forms.ValidationError("パスワードが一致しません")

        # print("clean処理は完了しました")
        return cleaned_data

    def save(self):
        user = super().save(commit=False)
        # print("saveメソッドが呼ばれました")
        user = User(
            email=self.cleaned_data.get("email"),
            username=self.cleaned_data.get("username"),
            gender_id=self.cleaned_data.get("gender").id,
            is_barrier_free=self.cleaned_data.get("is_barrier_free"),
        )
        validate_password(self.cleaned_data.get("password"), user)
        user.set_password(self.cleaned_data.get("password"))
        user.save()
        return user

class UserInfoUpdateForm(forms.ModelForm):

    gender = forms.ModelChoiceField(
        queryset=Gender.objects.all(), # DBデータの取得
        widget=forms.Select(attrs={"class": "border border-gray-400 focus:border-blue-500 focus:outline-none rounded-none bg-white"}),
        required=False,
        label="性別"
    )
    is_barrier_free = forms.BooleanField(
        required=False,
        label="バリアフリー優先",
        widget=forms.CheckboxInput(attrs={
            "class": "w-4 h-4" # チェックボックスのサイズ
        })
    )

    class Meta:
        model=User
        fields=["email", "username"]
        labels={
            "email": "メールアドレス",
            "username": "ユーザー名",
        }
        widgets = {
            "email": forms.EmailInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"}),
            "username": forms.TextInput(attrs={"class": "w-full max-w-md p-1 text-md ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"})
        }

    def __init__(self, *args, **kwargs):
        """現在のユーザー情報を初期値としてフォームにセット"""
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["email"].initial = user.email
            # print(user.email)
            self.fields["username"].initial = user.username
            self.fields["gender"].initial = user.gender
            self.fields["is_barrier_free"].initial = user.is_barrier_free

    def clean_email(self):
        """メールアドレスのバリデーション（重複しないようにする）"""
        email = self.cleaned_data["email"]
        # print("更新処理のメール", email)
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("このメールアドレスは既に使用されています")
        
        # print("メールアドレスの重複はありません。")
        return email

    def clean_username(self):
        """ユーザー名のバリデーション（重複しないようする）"""
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("このユーザー名は既に使用されています")
        
        # print("ユーザー名の重複はありません。")
        return username

class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="アカウント削除の注意事項を確認しました",
        widget=forms.CheckboxInput(attrs={
            "class": "w-4 h-4" # チェックボックスのサイズ
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        """ユーザーインスタンスを受け取る"""
        super().__init__(*args, **kwargs)
        self.user = user


    def save(self):
        """ユーザーを物理削除する"""
        if self.user:
            self.user.delete()
            # self.user.is_active=False
            # self.user.is_deleted=True
            # self.user.deleted_at=datetime.now()
            # self.user.save()














