from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from .models import User
from . import forms
from django.conf import settings
from django.http import JsonResponse
import json
import uuid
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

def user_login(request):
    login_form = forms.LoginForm()

    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)

        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'ログインしました。')
                print('ログインしました')
                
                # print(request.GET.get("next"))
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                else:
                    return render(request, 'toilet/home.html')
            else:
                messages.get_messages(request)
                messages.warning(request, 'メールアドレスかパスワードが間違っています')

    return render(request, 'accounts/user_login.html', context={
        'login_form': login_form,
        'liff_id': settings.LINE_LIFF_ID,
    })

def liff_login_view(request):
    if request.method == 'POST':
        print("django内、ラインユーザーのログイン認証を開始")
        try:
            # JSON形式のデータを解析
            data = json.loads(request.body)
            line_id = data.get('line_id')
            line_name = data.get('line_name')
            
            if not line_id:
                return JsonResponse({
                    'success': False,
                    'message': 'LINE IDが取得できませんでした。',
                    'redirect_url': reverse('accounts:user_login')
                })
            
            try:
                user = User.objects.get(line_id=line_id)
                # 既存ユーザーの場合、ログイン処理
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': f'{user.line_name or user.username}さん、おかえりなさい！',
                    'redirect_url': reverse('toilet:home')
                })
            except User.DoesNotExist:
                # 新規ユーザーの場合、アカウント作成
                username = f"user_{uuid.uuid4().hex[:8]}"
                
                while User.objects.filter(username=username).exists():
                    username = f"user_{uuid.uuid4().hex[:8]}"
                
                user = User.objects.create(
                    username=username,
                    line_id=line_id,
                    line_name=line_name,
                    is_active=True
                )
                
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': f'{line_name}さん、はじめまして！アカウントを作成しました。',
                    'redirect_url': reverse('toilet:home')
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '不正なリクエスト形式です。',
                'redirect_url': reverse('accounts:user_login')
            })
    
    # GETリクエストの場合
    return JsonResponse({
        'success': False,
        'message': '不正なアクセスです。',
        'redirect_url': reverse('accounts:user_login')
    })

def user_create(request):
    signin_form = forms.SigninForm()

    if request.method == 'POST':
        print("POSTデータ", request.POST)
        signin_form = forms.SigninForm(request.POST)

        if signin_form.is_valid():
            try:
                signin_form.save()
                return redirect('toilet:home')
            except ValidationError as e:
                signin_form.add_error('password', e)
                # print(type(e).__name__, e)
        else:
            print("ValidationError:", signin_form.errors)

    return render(request, 'accounts/user_create.html', context={
        'signin_form': signin_form,
        "liff_id": settings.LINE_LIFF_ID,
    })


@login_required
def user_logout(request):
    logout(request)
    # messages.success(request, 'ログアウトしました')
    print("ログアウトしました")
    return render(request, 'accounts/user_logout.html')


@login_required
def user_info_update(request):
    """ユーザー情報（ユーザー名&メールアドレス）更新"""
    if request.method == "POST":
        update_form = forms.UserInfoUpdateForm(request.POST, user=request.user, instance=request.user)

        if update_form.is_valid():
            update_form.save()
            print("ユーザー情報を更新しました。")
            return render(request, "accounts/user_info_update_done.html")

    else:
        update_form = forms.UserInfoUpdateForm(user=request.user, instance=request.user)

    # print("フォームの email 初期値:", update_form.fields["email"].initial)

    return render(request, "accounts/user_info_update.html", {"update_form": update_form})


def password_reset_request(request):
    """パスワードリセットリクエスト（メール送信）"""
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            print('email', email)

            try:
                user = User.objects.get(email=email)
                print("取得したuserID:", user.pk, str(user.pk))
                uid = urlsafe_base64_encode(str(user.pk).encode())
                print('uid', uid)
                token = default_token_generator.make_token(user)
                print('token', token)

                # フルパスのURL作成
                reset_url = request.build_absolute_uri(reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
                print('reset_url', reset_url)

                # メールのレンダリング
                subject = render_to_string('accounts/password_reset/subject.txt', {"user": user})
                message = render_to_string('accounts/password_reset/message.txt', {"reset_url": reset_url, "user":user})

                send_mail(subject, message, None, [user.email])
                # message.success(request, "パスワードリセットのメールを送信しました。")
                print("パスワードリセットのメールを送信しました。")

                return redirect("accounts:password_reset_done")

            except User.DoesNotExist:
                print("該当するユーザーが見つかりません")

    else:
        form = CustomPasswordResetForm()

    return render(request, 'accounts/password_reset/password_reset_form.html', {"form": form})

def password_reset_done(request):
    """パスワードリセットメール送信完了ページ"""
    return render(request, 'accounts/password_reset/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """新しいパスワード設定ページ"""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        print('password_reset_confirmのuid', uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) :
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "パスワードが変更されました。")
                print("パスワードが変更されました。")
                return redirect("accounts:password_reset_complete")
        else:
            form = CustomSetPasswordForm(user)

        return render(request, "accounts/password_reset/password_reset_confirm.html", {"form": form})
    
    else:
        # messages.error(request, "リンクが無効または期限切れです。")
        print("リンクが無効または期限切れです。")
        return redirect("accounts:password_reset_request")
    
def password_reset_complete(request):
    """パスワードリセット完了ページ"""
    return render(request, "accounts/password_reset/password_reset_complete.html")

@login_required
def user_delete(request):
    if request.method == "POST":
        delete_form = forms.UserDeleteForm(request.POST, user=request.user)
        if delete_form.is_valid() and delete_form.cleaned_data.get("confirm"):
            delete_form.save() # 物理削除する
            logout(request)
            # print("アカウントが削除されました")
            return redirect("toilet:home")
    else:
        delete_form = forms.UserDeleteForm()

    return render(request, "accounts/user_delete.html", {"delete_form": delete_form})

