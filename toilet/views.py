from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from . import forms
from django.http import JsonResponse
from .models import TrainLine, TrainStation, ToiletMaster, MaleToilet, FemaleToilet, MultiFunctionalToilet, ToiletStall, MaleToiletComments, FemaleToiletComments, MultifunctionalToiletComments
from decimal import Decimal, ROUND_DOWN
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from accounts.models import Gender, User
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import Http404
from django.conf import settings
from itertools import chain
from operator import attrgetter


# liffでアクセスする際に必要
def liff_entrypoint(request):
    context = {
        "liff_id": settings.LINE_LIFF_ID,
    }
    return render(request, 'toilet/liff_entry.html', context)

def home(request):
    print("LINE_LIFF_ID", settings.LINE_LIFF_ID)
    context = {
        "liff_id": settings.LINE_LIFF_ID,
    }
    return render(request, 'toilet/home.html', context)

def search_toilet(request):
    if request.method == 'POST':
        search_form = forms.SearchStation(request.POST)
        station_id = request.POST.get("station_id")
        # print("受け取ったPOSTデータ:", request.POST)
        # print("選択された駅ID:", station_id)

        station_id = request.POST.get("station_id")
        # 検索のidをセッションに保存する
        request.session["search_station_id"] = station_id

        # DBから該当するトイレを取得する
        toilets = ToiletMaster.objects.filter(station_id=station_id)
        male_toilets = MaleToilet.objects.filter(toilet_id__station_id=station_id)
        female_toilets = FemaleToilet.objects.filter(toilet_id__station_id=station_id)
        multifunctional_toilets = MultiFunctionalToilet.objects.filter(toilet_id__station_id=station_id)

        # 一致したトイレ情報を格納するリスト
        toilet_data = []

        # 各トイレの場所と照合して、データを収集
        for toilet in toilets:
            toilet_place = toilet.place
            matched_male = male_toilets.filter(toilet_id__place=toilet_place).first()
            matched_female = female_toilets.filter(toilet_id__place=toilet_place).first()
            matched_multifunctional = multifunctional_toilets.filter(toilet_id__place=toilet_place).first()

            # 一致したデータをリストに格納
            toilet_data.append({
                "place": toilet_place,
                "male": matched_male,
                "female": matched_female,
                "multifunctional": matched_multifunctional
            })

        return render(request, 'toilet/search_result.html', context={
            'toilet_data': toilet_data
        })
        # else:
            # print("フォームエラー:", search_form.errors) # エラーの確認
    else:
        search_form = forms.SearchStation()

    return render(request, 'toilet/search_toilet.html', context={
            'search_form': search_form,
        }
    )

def suggest_station(request):
    """駅名検索時の駅候補機能（DBから参照する）"""

    query = request.GET.get("query", "")
    # print(query) # 入力された文字列を受け取る
    if query:
        # icontainsを使って入力された文字をもとに部分一致検索
        stations = TrainStation.objects.filter(Q(station_name_japanese__icontains=query) | Q(station_name__icontains=query)).values(
            "id", "station_name", "train_line__train_line_name", "train_line__railway_company"
        )

        # print(list(stations))

        return JsonResponse({"suggestions": list(stations)})

    return JsonResponse({"suggestions": []})

def toilet_info(request, pk, gender):
    # print("pk", pk)
    # print("gender", gender)

    try:
        if gender == 1:
            toilet = get_object_or_404(MaleToilet, pk=pk)
            toilet_stall = get_object_or_404(ToiletStall, male_toilet_id=toilet)
            comments = MaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).order_by("data_create").reverse()
            if not comments.exists():
                print("コメントはありません")
                comments = ""
            toilet_info = [
                ("改札内外", toilet.toilet_id.station_ticket_gate_id),
                ("設置階", toilet.toilet_id.floor),
                ("利用時間", toilet.toilet_id.get_opening_hours),
                ("個室数", {"洋式": toilet_stall.western_style, "和式": toilet_stall.japanese_style}),
                ("小便器数", toilet.urial),
                ("近い改札口", toilet.toilet_id.near_gate),
                ("近いホーム", toilet.toilet_id.near_home_num),
                ("近い車両番号", toilet.toilet_id.near_train_car_num),
                ("パウダールーム", toilet.powder_room_display),
                ("温水洗浄便座", toilet.warm_water_washing_toilet_seat_display),
                ("チャイルドシート", toilet.child_seat_display),
                ("おむつ交換設備", toilet.child_facility_display),
                ("バリアフリートイレ", toilet.barrier_free_toilet_display),
                ("車いす対応", toilet.wheelchair_display),
                ("姿見", toilet.full_length_mirror_display),
                ("フィッティングボード", toilet.fitting_board_display),
                ("ゴミ箱", toilet.trash_can_display),
            ]
        elif gender == 2:
            toilet = get_object_or_404(FemaleToilet, pk=pk)
            toilet_stall = get_object_or_404(ToiletStall, female_toilet_id=toilet)
            comments = FemaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).order_by("data_create").reverse()
            if not comments.exists():
                print("コメントはありません")
                comments = ""
            toilet_info = [
                ("改札内外", toilet.toilet_id.station_ticket_gate_id),
                ("設置階", toilet.toilet_id.floor),
                ("利用時間", toilet.toilet_id.get_opening_hours),
                ("個室数", {"洋式": toilet_stall.western_style, "和式": toilet_stall.japanese_style}),
                ("近い改札口", toilet.toilet_id.near_gate),
                ("近いホーム", toilet.toilet_id.near_home_num),
                ("近い車両番号", toilet.toilet_id.near_train_car_num),
                ("パウダールーム", toilet.powder_room_display),
                ("温水洗浄便座", toilet.warm_water_washing_toilet_seat_display),
                ("チャイルドシート", toilet.child_seat_display),
                ("おむつ交換設備", toilet.child_facility_display),
                ("バリアフリートイレ", toilet.barrier_free_toilet_display),
                ("車いす対応", toilet.wheelchair_display),
                ("姿見", toilet.full_length_mirror_display),
                ("フィッティングボード", toilet.fitting_board_display),
                ("ゴミ箱", toilet.trash_can_display),
            ]
        elif gender == 3:
            toilet = get_object_or_404(MultiFunctionalToilet, pk=pk)
            toilet_stall = get_object_or_404(ToiletStall, multi_toilet_id=toilet)
            comments = MultifunctionalToiletComments.objects.filter(toilet=toilet.pk, gender=gender).order_by("data_create").reverse()
            if not comments.exists():
                print("コメントはありません")
                comments = ""
            toilet_info = [
                ("改札内外", toilet.toilet_id.station_ticket_gate_id),
                ("設置階", toilet.toilet_id.floor),
                ("利用時間", toilet.toilet_id.get_opening_hours),
                ("個室数", {"洋式": toilet_stall.western_style, "和式": toilet_stall.japanese_style}),
                ("近い改札口", toilet.toilet_id.near_gate),
                ("近いホーム", toilet.toilet_id.near_home_num),
                ("近い車両番号", toilet.toilet_id.near_train_car_num),
                ("温水洗浄便座", toilet.warm_water_washing_toilet_seat_display),
                ("チャイルドシート", toilet.child_seat_display),
                ("おむつ交換設備", toilet.child_facility_display),
                ("バリアフリートイレ", toilet.barrier_free_toilet_display),
                ("車いす対応", toilet.wheelchair_display),
                ("姿見", toilet.full_length_mirror_display),
                ("フィッティングボード", toilet.fitting_board_display),
                ("ゴミ箱", toilet.trash_can_display),
            ]

        station_name = toilet.toilet_id.station_id.station_name
        place = toilet.toilet_id.place
        value = Decimal(toilet.value)
        value = value.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
        size = Decimal(toilet.size)
        size = size.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
        congestion = Decimal(toilet.congestion)
        congestion = congestion.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
        root = toilet.toilet_id.toilet_root

        return render(request, 'toilet/search_result_toilet_info.html', {
            "toilet": toilet,
            "station_name": station_name,
            "place": place,
            "value": value,
            "size": size,
            "congestion": congestion,
            "toilet_info": toilet_info,
            "root": root,
            "gender": gender,
            "comments": comments,
        })

    except Exception as e:
        print("データを取得出来ませんでした", e)
        return render(request, 'toilet/search_result_toilet_info.html', {})


def change_toilet_data(request, toilet_pk, gender_num):

    # print("toilet_pk", toilet_pk)
    # print("gender_num", gender_num)

    try:
        if gender_num == 1:
            toilet = get_object_or_404(MaleToilet, toilet_id=toilet_pk)
            urial = toilet.urial
            toilet_stall = get_object_or_404(ToiletStall, male_toilet_id=toilet)
            powder_room = toilet.powder_room_display()
            comments = MaleToiletComments.objects.select_related("user").filter(gender=gender_num, toilet=toilet.pk).order_by("data_create").reverse()
        elif gender_num == 2:
            toilet = get_object_or_404(FemaleToilet, toilet_id=toilet_pk)
            toilet_stall = get_object_or_404(ToiletStall, female_toilet_id=toilet)
            powder_room = toilet.powder_room_display()
            comments = FemaleToiletComments.objects.select_related("user").filter(gender=gender_num, toilet=toilet.pk).order_by("data_create").reverse()
            # print(comments)
        elif gender_num == 3:
            toilet = get_object_or_404(MultiFunctionalToilet, toilet_id=toilet_pk)
            toilet_stall = get_object_or_404(ToiletStall, multi_toilet_id=toilet)
            comments = MultifunctionalToiletComments.objects.select_related("user").filter(gender=gender_num, toilet=toilet.pk).order_by("data_create").reverse()
        else:
            return JsonResponse({"error": "無効なgender値です"}, status=400)
    except Exception as e:
        print("データを取得出来ませんでした")
        return JsonResponse({"error": f"データを取得できませんでした。存在しないデータの可能性があります。:{str(e)}"}, status=500)

    # print("toilet", toilet)

    # トイレpk(ToiletMasterテーブルのpk)
    toilet_pk = toilet.toilet_id.pk
    # トイレid(各性別のトイレテーブルのid)
    toilet_id = toilet.pk
    # 駅名
    station_name = toilet.toilet_id.station_id.station_name
    # トイレ場所
    place = toilet.toilet_id.place
    # 改札内外
    in_out_station_ticket_gate = toilet.toilet_id.station_ticket_gate_id.station_ticket_gate
    # 評価
    value = Decimal(toilet.value)
    value = value.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
    # 広さ
    size = Decimal(toilet.size)
    size = size.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
    # 混雑さ
    congestion = Decimal(toilet.congestion)
    congestion = congestion.quantize(Decimal("0.0"), rounding=ROUND_DOWN)
    # 設置階
    floor = toilet.toilet_id.floor
    # 利用時間
    time = toilet.toilet_id.get_opening_hours()
    # 近い改札口
    near_gate = toilet.toilet_id.near_gate
    # 近いホーム
    near_home_num = toilet.toilet_id.near_home_num
    # 近い車両番号
    near_train_car_num = toilet.toilet_id.near_train_car_num
    # 温水洗浄便座
    warm_water_washing_toilet_seat = toilet.warm_water_washing_toilet_seat_display()
    # チャイルドシート
    child_seat = toilet.child_seat_display()
    # おむつ交換設備
    child_facility = toilet.child_facility_display()
    # バリアフリートイレ
    barrier_free_toilet = toilet.barrier_free_toilet_display()
    # 車いす対応
    wheelchair = toilet.wheelchair_display()
    # 姿見
    full_length_mirror = toilet.full_length_mirror_display()
    # フィッティングボード
    fitting_board = toilet.fitting_board_display()
    # ゴミ箱
    trash_can = toilet.trash_can_display()
    # 経路
    root = toilet.toilet_id.toilet_root
    # 性別id
    gen = toilet.gender.pk

    if comments.exists():
        comments = list(comments.values(
            "user",
            "user__username",
            "comment",
            "value",
            "size",
            "congestion",
            "data_create"
        ))
    else:
        comments = ""


    # javascriptでデータを受け取るには、Json形式でレスポンスするのが一般的で、適しているため、JsonResponseを使用する。
    if gender_num == 1:
        toilet_info = [
            {"label": "改札内外", "value": in_out_station_ticket_gate},
            {"label": "設置階", "value": floor},
            {"label": "利用時間", "value": time},
            {"label": "個室数", "value": {"洋式": toilet_stall.western_style, "和式": toilet_stall.japanese_style}},
            {"label": "小便器数", "value": urial},
            {"label": "近い改札口", "value": near_gate},
            {"label": "近いホーム", "value": near_home_num},
            {"label": "近い車両番号", "value": near_train_car_num},
            {"label": "パウダールーム", "value": powder_room},
            {"label": "温水洗浄便座", "value": warm_water_washing_toilet_seat},
            {"label": "チャイルドシート", "value": child_seat},
            {"label": "おむつ交換設備", "value": child_facility},
            {"label": "バリアフリートイレ", "value": barrier_free_toilet},
            {"label": "車いす対応", "value": wheelchair},
            {"label": "姿見", "value": full_length_mirror},
            {"label": "フィッティングボード", "value": fitting_board},
            {"label": "ゴミ箱", "value": trash_can},
        ]
    elif gender_num == 2:
        toilet_info = [
            {"label": "改札内外", "value": in_out_station_ticket_gate},
            {"label": "設置階", "value": floor},
            {"label": "利用時間", "value": time},
            {"label": "個室数", "value": {"洋式": toilet_stall.western_style, "和式": toilet_stall.japanese_style}},
            {"label": "近い改札口", "value": near_gate},
            {"label": "近いホーム", "value": near_home_num},
            {"label": "近い車両番号", "value": near_train_car_num},
            {"label": "パウダールーム", "value": powder_room},
            {"label": "温水洗浄便座", "value": warm_water_washing_toilet_seat},
            {"label": "チャイルドシート", "value": child_seat},
            {"label": "おむつ交換設備", "value": child_facility},
            {"label": "バリアフリートイレ", "value": barrier_free_toilet},
            {"label": "車いす対応", "value": wheelchair},
            {"label": "姿見", "value": full_length_mirror},
            {"label": "フィッティングボード", "value": fitting_board},
            {"label": "ゴミ箱", "value": trash_can},
        ]
    elif gender_num == 3:
        toilet_info = [
            {"label": "改札内外", "value": in_out_station_ticket_gate},
            {"label": "設置階", "value": floor},
            {"label": "利用時間", "value": time},
            {"label": "個室数", "value": {"洋式": toilet_stall.western_style, "和式": toilet_stall.japanese_style}},
            {"label": "近い改札口", "value": near_gate},
            {"label": "近いホーム", "value": near_home_num},
            {"label": "近い車両番号", "value": near_train_car_num},
            {"label": "温水洗浄便座", "value": warm_water_washing_toilet_seat},
            {"label": "チャイルドシート", "value": child_seat},
            {"label": "おむつ交換設備", "value": child_facility},
            {"label": "バリアフリートイレ", "value": barrier_free_toilet},
            {"label": "車いす対応", "value": wheelchair},
            {"label": "姿見", "value": full_length_mirror},
            {"label": "フィッティングボード", "value": fitting_board},
            {"label": "ゴミ箱", "value": trash_can},
        ]

    print("レスポンス前")
    return JsonResponse({
        "toilet": {
            "toilet_pk": toilet_pk,
            "id": toilet_id, # 各性別のトイレpk
            "station_name": station_name,
            "place": place,
            "value": value,
            "size": size,
            "congestion": congestion,
            "toilet_info": toilet_info,
            "root": root,
            "gender": gen,
            "comments": comments,
        },
    })

@login_required(login_url='/accounts/user_login')
def toilet_review(request, toilet_id, gender):
    "レビューボタン押されたときの処理"

    print("toilet_id:", toilet_id)
    print("gender:", gender)
    print("user:", request.user.pk)

    try:
        if gender == 1:
            toilet = get_object_or_404(MaleToilet, toilet_id=toilet_id)
            print("toilet: ", toilet)
        elif gender == 2:
            toilet = get_object_or_404(FemaleToilet, toilet_id=toilet_id)
        elif gender == 3:
            toilet = get_object_or_404(MultiFunctionalToilet, toilet_id=toilet_id)
        else:
            print("gender値が不正です")
            raise ValueError(f"不正なgender値:{gender}")

        if toilet is None:
            raise ValueError(f"toilet_id={toilet_id} のデータが見つかりません")

        if request.method == 'POST':
            if gender == 1:
                review_form = forms.MaleToiletReviewForm(request.POST)
            elif gender == 2:
                review_form = forms.FemaleToiletReviewForm(request.POST)
            elif gender == 3:
                review_form = forms.MultifunctionalToiletReviewForm(request.POST)

            if review_form.is_valid():
                gender_instance = get_object_or_404(Gender, pk=gender)
                user_instance = get_object_or_404(User, pk=request.user.pk)
                toilet_instance = get_object_or_404(ToiletMaster, pk=toilet_id)

                if gender == 1:
                    male_toilet_instance = get_object_or_404(MaleToilet, toilet_id=toilet_id)
                    comment_data = MaleToiletComments.objects.create(
                        user=user_instance,
                        comment=review_form.cleaned_data["comment"],
                        gender=gender_instance,
                        value=review_form.cleaned_data["value"],
                        size=review_form.cleaned_data["size"],
                        congestion=review_form.cleaned_data["congestion"],
                        toilet=male_toilet_instance,
                    )
                    print("ここまできている")
                elif gender == 2:
                    female_toilet_instance = get_object_or_404(FemaleToilet, toilet_id=toilet_id)
                    comment_data = FemaleToiletComments.objects.create(
                        user=user_instance,
                        comment=review_form.cleaned_data["comment"],
                        gender=gender_instance,
                        value=review_form.cleaned_data["value"],
                        size=review_form.cleaned_data["size"],
                        congestion=review_form.cleaned_data["congestion"],
                        toilet=female_toilet_instance,
                    )
                elif gender == 3:
                    multi_toilet_instance = get_object_or_404(MultiFunctionalToilet, toilet_id=toilet_id)
                    comment_data = MultifunctionalToiletComments.objects.create(
                        user=user_instance,
                        comment=review_form.cleaned_data["comment"],
                        gender=gender_instance,
                        value=review_form.cleaned_data["value"],
                        size=review_form.cleaned_data["size"],
                        congestion=review_form.cleaned_data["congestion"],
                        toilet=multi_toilet_instance,
                    )

                data_dict = {
                    "value": review_form.cleaned_data["value"],
                    "size": review_form.cleaned_data["size"],
                    "congestion": review_form.cleaned_data["congestion"],
                    "gender": gender,
                    "toilet_id": toilet_id, # toilet_idはToiletMasterテーブルのpk
                }
                calculate_value_size_congestion(data_dict['gender'], data_dict['toilet_id'])

                return redirect('toilet:toilet_info', pk=toilet.pk, gender=gender)
        else:
            print("GETメソッド")
            try:
                if gender == 1:
                    review_form = forms.MaleToiletReviewForm()
                elif gender == 2:
                    review_form = forms.FemaleToiletReviewForm()
                elif gender == 3:
                    review_form = forms.MultifunctionalToiletReviewForm()
            except Exception as e:
                print("フォーム生成エラー: ", e)
                raise e

        return render(request, 'toilet/toilet_review.html', context={
                'toilet': toilet,
                'review_form': review_form,
            }
        )

    except ValueError as e:
        return HttpResponseBadRequest(f"不正な値が指定されました: {e}")
    
    except Http404 as e:
        return render(request, 'toilet/toilet_get_review_error.html', {
            "message": "指定されたトイレ情報は見つかりませんでした。"
        }, status=404)
    
    except Exception as e:
        print("予期しないエラー: ", e)
        return render(request, "toilet/toilet_get_review_error.html", {
            "message": "予期しないエラーが発生しました。",
            "error": str(e)
        }, status=500)
    
def calculate_value_size_congestion(gender, toilet_id):

    if gender == 1:
        # きれいさ
        initial_value = MaleToilet.objects.filter(toilet_id=toilet_id).first().initial_value # 初期データ
        total_value = MaleToilet.objects.filter(toilet_id=toilet_id).first().value

        # 広さの平均を算出
        initial_size = MaleToilet.objects.filter(toilet_id=toilet_id).first().initial_size # 初期データ
        total_size = MaleToilet.objects.filter(toilet_id=toilet_id).first().size

        # 空き具合の平均を算出
        initial_congestion = MaleToilet.objects.filter(toilet_id=toilet_id).first().initial_congestion # 初期データ
        total_congestion = MaleToilet.objects.filter(toilet_id=toilet_id).first().congestion

        toilet = MaleToilet.objects.filter(toilet_id=toilet_id).first()

        # コメントの数 + デフォルトで最初に登録されているデータ1件
        length = (MaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).count() + 1)

        # きれいさ
        comment_total_value_dict = MaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('value'))

        # 広さ
        comment_total_size_dict = MaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('size'))

        # 空き具合
        comment_total_congestion_dict = MaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('congestion'))

    elif gender == 2:
        # きれいさ
        initial_value = FemaleToilet.objects.filter(toilet_id=toilet_id).first().initial_value # 初期データ
        total_value = FemaleToilet.objects.filter(toilet_id=toilet_id).first().value

        # 広さの平均を算出
        initial_size = FemaleToilet.objects.filter(toilet_id=toilet_id).first().initial_size # 初期データ
        total_size = FemaleToilet.objects.filter(toilet_id=toilet_id).first().size

        # 空き具合の平均を算出
        initial_congestion = FemaleToilet.objects.filter(toilet_id=toilet_id).first().initial_congestion # 初期データ
        total_congestion = FemaleToilet.objects.filter(toilet_id=toilet_id).first().congestion

        toilet = FemaleToilet.objects.filter(toilet_id=toilet_id).first()

        # コメントの数 + デフォルトで最初に登録されているデータ1件
        length = (FemaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).count() + 1)

        # きれいさ
        comment_total_value_dict = FemaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('value'))

        # 広さ
        comment_total_size_dict = FemaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('size'))

        # 空き具合
        comment_total_congestion_dict = FemaleToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('congestion'))

    elif gender == 3:
        # きれいさ
        initial_value = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first().initial_value # 初期データ
        total_value = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first().value

        # 広さの平均を算出
        initial_size = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first().initial_size # 初期データ
        total_size = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first().size

        # 空き具合の平均を算出
        initial_congestion = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first().initial_congestion # 初期データ
        total_congestion = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first().congestion

        toilet = MultiFunctionalToilet.objects.filter(toilet_id=toilet_id).first()
    
        # コメントの数 + デフォルトで最初に登録されているデータ1件
        length = (MultifunctionalToiletComments.objects.filter(toilet=toilet.pk, gender=gender).count() + 1)

        # きれいさ
        comment_total_value_dict = MultifunctionalToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('value'))

        # 広さ
        comment_total_size_dict = MultifunctionalToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('size'))

        # 空き具合
        comment_total_congestion_dict = MultifunctionalToiletComments.objects.filter(toilet=toilet.pk, gender=gender).aggregate(Sum('congestion'))
    
    else:
        raise ValueError("不正gender値が設定されました")

    # きれいさの総合値
    comment_total_value = comment_total_value_dict['value__sum'] or 0
    # print("comment_total_value", comment_total_value)

    total_value = (comment_total_value + initial_value) / length
    # print("total_value", total_value)

    # 広さの総合値
    comment_total_size = comment_total_size_dict['size__sum'] or 0
    # print("comment_total_size", comment_total_size)

    total_size = (comment_total_size + initial_size) / length
    # print("total_size", total_size)

    # 空き具合の総合値
    comment_total_congestion = comment_total_congestion_dict['congestion__sum'] or 0
    # print("comment_total_congestion", comment_total_congestion)

    total_congestion = (comment_total_congestion + initial_congestion) / length
    # print("total_congestion", total_congestion)

    # データ更新
    toilet.value = round(total_value, 1)
    toilet.size = round(total_size, 1)
    toilet.congestion = round(total_congestion, 1)
    toilet.save()


def toilet_rank(request):
    # ホーム画面でランキングを見るボタンが押された時の処理

    if request.method == "POST":
        search_line_form = forms.SearchLine(request.POST)

        line = request.POST.get("line")
        gender = request.POST.get("gender")
        toilets = get_toilet_rank_queryset(request, line, gender)

        line_obj = TrainLine.objects.filter(pk=line).first

        return render(request, 'toilet/toilet_rank.html', context={
            "line":line_obj,
            "toilets": toilets,
            "gender": gender,
            "search_line_form": search_line_form,
        })

    else:
        search_line_form = forms.SearchLine()
        return render(request, 'toilet/toilet_rank.html', context={
            "search_line_form": search_line_form,
        })

def get_toilet_object_rank(request, line, gender):
    # ランキング画面で性別ボタンが押された時の処理

    gender = int(gender)

    try:
        toilets = get_toilet_rank_queryset(request, line, gender)
        print("toilets['is_end']:", toilets["is_end"])
        return JsonResponse ({
            "toilets": {
                "toilet_value": list(toilets["toilet_value"].values("toilet_id", "toilet_id__station_id__station_name", "toilet_id__place", "toilet_id__station_id__train_line__railway_company", "value")),

                "toilet_size": list(toilets["toilet_size"].values("toilet_id", "toilet_id__station_id__station_name", "toilet_id__place", "toilet_id__station_id__train_line__railway_company", "size")),

                "toilet_congestion": list(toilets["toilet_congestion"].values("toilet_id", "toilet_id__station_id__station_name", "toilet_id__place", "toilet_id__station_id__train_line__railway_company", "congestion")),
            },
            "gender": gender,
            "is_end": toilets["is_end"]
        })
    except ValueError:
        return JsonResponse({"error": "無効なgender"}, status=400)
        

def get_toilet_rank_queryset(request, line, gender):
    gender = int(gender)
    display_count = int(request.GET.get("count", 5))
    

    if gender == 1:
        # 男性トイレのオブジェクトを取得
        all_obj = MaleToilet.objects.filter(toilet_id__station_id__train_line=line)

    elif gender == 2:
        # 女性トイレのオブジェクトを取得
        all_obj = FemaleToilet.objects.filter(toilet_id__station_id__train_line=line)

    elif gender == 3:
        # 多機能トイレのオブジェクトを取得
        all_obj = MultiFunctionalToilet.objects.filter(toilet_id__station_id__train_line=line)

    else:
        raise ValueError("不正gender値が設定されました")
    
    is_end = display_count >= all_obj.count()
    print("is_end:", is_end) # 最後までデータを取得出来たらtrueになる
    return {
        "toilet_value": all_obj.order_by('value').reverse()[:display_count],
        "toilet_size": all_obj.order_by('size').reverse()[:display_count],
        "toilet_congestion": all_obj.order_by('congestion').reverse()[:display_count],
        "is_end": is_end
    }

def get_latest_comment(request):
    male_comments = MaleToiletComments.objects.filter(gender=1).order_by("data_create").reverse()
    female_comments = FemaleToiletComments.objects.filter(gender=2).order_by("data_create").reverse()
    multi_comments = MultifunctionalToiletComments.objects.filter(gender=3).order_by("data_create").reverse()
    
    print(multi_comments)
    return render(request, "toilet/toilet_latest_comment.html", context={
        "male_comments": male_comments,
        "female_comments": female_comments,
        "multi_comments": multi_comments
    })

@login_required
def user_comments(request):
    user = request.user
    print(user)

    # 各コメントを取得
    male_comments = MaleToiletComments.objects.filter(user=user)
    female_comments = FemaleToiletComments.objects.filter(user=user)
    multi_comments = MultifunctionalToiletComments.objects.filter(user=user)

    # 3つのクエリセットを結合
    all_comments = chain(male_comments, female_comments, multi_comments)

    # 降順ソート（上から新しい順）
    sorted_comments = sorted(all_comments, key=attrgetter("data_create"), reverse=True)

    # ページネーション処理
    paginator = Paginator(sorted_comments, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "toilet/user_comments.html", {'page_obj': page_obj})

def toilet_review_revise(request, pk, gender):
    user = request.user
    if gender == 1:
        comment = get_object_or_404(MaleToiletComments, pk=pk, user=user)
        print("comment", comment.toilet)
        print("comment", comment.comment)
    elif gender == 2:
        comment = get_object_or_404(FemaleToiletComments, pk=pk, user=user)
        print("comment", comment.toilet)
        print("comment", comment.comment)
    elif gender == 3:
        comment = get_object_or_404(MaleToiletComments, pk=pk, user=user)
        print("comment", comment.toilet)
        print("comment", comment.comment)

    if request.method == "POST":
        if gender == 1:
            form = forms.MaleToiletReviewForm(request.POST, instance=comment)
        elif gender == 2:
            form = forms.FemaleToiletReviewForm(request.POST, instance=comment)
        elif gender == 3:
            form = forms.MultifunctionalToiletReviewForm(request.POST, instance=comment)
        gender_pk = gender
        toilet_pk = comment.toilet.pk
        toilet_id = comment.toilet.toilet_id # 各性別トイレテーブルが持つtoilet_id(ToiletMasterテーブルのpkでもある)

        if gender_pk == 1:
            toilet_obj = MaleToilet.objects.filter(pk=toilet_pk).first()
            # t_pk = toilet_obj.pk
        elif gender_pk == 2:
            toilet_obj = FemaleToilet.objects.filter(pk=toilet_pk).first()
            # t_pk = toilet_obj.pk
        elif gender_pk == 3:
            toilet_obj = MultiFunctionalToilet.objects.filter(pk=toilet_pk).first()

        t_pk = toilet_obj.pk

        try:
            if form.is_valid():
                form.save()
                calculate_value_size_congestion(gender_pk, toilet_id)
                return redirect("toilet:toilet_info", pk=t_pk, gender=gender_pk)

        except Exception as e:
            print("e", e)
    else:
        if gender == 1:
            review_form = forms.MaleToiletReviewForm(instance=comment)
        elif gender == 2:
            review_form = forms.FemaleToiletReviewForm(instance=comment)
        elif gender == 3:
            review_form = forms.MultifunctionalToiletReviewForm(instance=comment)

    return render(request, "toilet/toilet_review_revise.html", context={
        "review_form": review_form,
        "comment": comment,
    })

def toilet_review_delete(request, pk, gender):
    user = request.user
    if gender == 1:
        comment = get_object_or_404(MaleToiletComments, pk=pk, user=user)
        print("comment", comment.toilet)
        print("comment", comment.comment)
    elif gender == 2:
        comment = get_object_or_404(FemaleToiletComments, pk=pk, user=user)
        print("comment", comment.toilet)
        print("comment", comment.comment)
    elif gender == 3:
        comment = get_object_or_404(MaleToiletComments, pk=pk, user=user)
        print("comment", comment.toilet)
        print("comment", comment.comment)

    gender_pk = gender
    toilet_pk = comment.toilet.pk
    toilet_id = comment.toilet.toilet_id # 各性別トイレテーブルが持つtoilet_id(ToiletMasterテーブルのpkでもある)

    if gender_pk == 1:
        toilet_obj = MaleToilet.objects.filter(pk=toilet_pk).first()
        t_pk = toilet_obj.pk
    elif gender_pk == 2:
        toilet_obj = FemaleToilet.objects.filter(pk=toilet_pk).first()
        t_pk = toilet_obj.pk
    elif gender_pk == 3:
        toilet_obj = MultiFunctionalToilet.objects.filter(pk=toilet_pk).first()
        t_pk = toilet_obj.pk

    try:
        comment.delete()
        calculate_value_size_congestion(gender_pk, toilet_id)
        return redirect("toilet:toilet_info", pk=t_pk, gender=gender_pk)
    except Exception as e:
        print("e", e)

