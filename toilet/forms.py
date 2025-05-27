from django import forms
from .models import TrainLine, ToiletMaster, MaleToiletComments, FemaleToiletComments, MultifunctionalToiletComments
from toilet.models import Gender

class SearchStation(forms.Form):
    station_name = forms.CharField(
        label="駅名を検索",
        max_length=30,
        widget=forms.TextInput(attrs={
            "id": "station_input",
            "class": "block w-full p-2 ring-1 ring-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none",
            "autocomplete": "off", # ブラウザの自動補完機能をオフにして、過去の入力値が候補として表示されないようにする。
            "placeholder": "入力候補から選択してください"
        })
    )

class BaseReviewForm(forms.ModelForm):
    value = forms.IntegerField(
        label="きれいさ",
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={
            "step":1,
            "placeholder": "1～5",
            "class": "w-full p-1 ring-1 ring-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none",
        }),
    )
    size = forms.IntegerField(
        label="広さ",
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={
            "step":1,
            "placeholder": "1～5",
            "class": "w-full p-1 ring-1 ring-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none",
        }),
    )
    congestion = forms.IntegerField(
        label="空き具合",
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={
            "step":1,
            "placeholder": "1～5",
            "class": "w-full p-1 ring-1 ring-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none",
        }),
    )
    comment = forms.CharField(
        label="コメント",
        max_length=300,
        widget=forms.Textarea(attrs={
            "class": "w-full p-1 ring-1 ring-gray-500 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none"
        }),

    )

    class Meta:
        fields = ['value', 'size', 'congestion', 'comment']

class MaleToiletReviewForm(BaseReviewForm):
    # モデルと連携させることで、Commentモデルに連携されたフォームを作成 -> 登録データが入力された状態のフォームを表示できる。女性、多機能も同様
    class Meta(BaseReviewForm.Meta):
        model = MaleToiletComments

class FemaleToiletReviewForm(BaseReviewForm):
    class Meta(BaseReviewForm.Meta):
        model = FemaleToiletComments

class MultifunctionalToiletReviewForm(BaseReviewForm):
    class Meta(BaseReviewForm.Meta):
        model = MultifunctionalToiletComments

class SearchLine(forms.Form):
    line = forms.ModelChoiceField(
        queryset=TrainLine.objects.all(),
        widget=forms.Select(attrs={
            "id": "line_input",
            "class": "w-full sm:w-2/5 p-1 ring-1 ring-gray-400 focus:ring-1 focus:ring-blue-500 focus:outline-none rounded-none bg-white"
        }),
        label="路線",
        empty_label="路線を選択してください",
        required=True,
        error_messages={"required": "路線を選択してください"}
    )
    gender = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = [(g.pk, g.type) for g in Gender.objects.all()]


