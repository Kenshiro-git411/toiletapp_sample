from django.db import models
from accounts.models import User, Gender
from django.utils import timezone
from django.core.exceptions import ValidationError

class TrainLine(models.Model):
    """路線マスターテーブル"""

    train_line_name = models.CharField(max_length=255)
    railway_company = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.train_line_name

class TrainStation(models.Model):
    """駅マスターテーブル"""

    station_name = models.CharField(max_length=255)
    station_name_japanese = models.CharField(max_length=255)
    train_line = models.ForeignKey(TrainLine, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.station_name}({self.train_line})"

class StationTicketGate(models.Model):
    """改札内外マスターテーブル"""

    station_ticket_gate = models.CharField(max_length=5)

    def __str__(self):
        return self.station_ticket_gate

class ToiletMaster(models.Model):
    """トイレマスターテーブル"""

    station_id = models.ForeignKey(TrainStation, on_delete=models.CASCADE)
    place = models.CharField(max_length=30)
    station_ticket_gate_id = models.ForeignKey(StationTicketGate, on_delete=models.SET_NULL, null=True)
    # open_timeとclose_timeを文字列の始発~終電の記載にする方法を確認するAPI
    open_time = models.TimeField(auto_now=False, null=True)
    close_time = models.TimeField(auto_now=False, null=True)
    floor = models.CharField(max_length=5, help_text="設置されている階を数字で入力してください")
    near_gate = models.CharField(max_length=100)
    near_home_num = models.CharField(max_length=30)
    near_train_car_num = models.CharField(max_length=50)
    toilet_root = models.TextField(null=True)

    def __str__(self):
        return f"{self.station_id.train_line.railway_company}{self.station_id.station_name}({self.place})"

    def get_opening_hours(self):
        """営業時間を 'HH:MM～HH:MM' の形式で取得"""
        return f"{self.open_time.strftime('%H:%M')}～{self.close_time.strftime('%H:%M')}"

class MaleToilet(models.Model):
    """男性用トイレテーブル"""

    toilet_id = models.ForeignKey(ToiletMaster, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    # 初期データ(きれいさ)
    initial_value = models.FloatField(null=True)
    # 初期データ(広さ)
    initial_size = models.FloatField(null=True)
    # 初期データ(きれいさ)
    initial_congestion = models.FloatField(null=True)
    # きれいさ(平均値:随時更新)
    value = models.FloatField(null=True)
    # 広さ(平均値:随時更新)
    size = models.FloatField(null=True)
    # 空き具合(平均値:随時更新)
    congestion = models.FloatField(null=True)
    # 小便器
    urial = models.IntegerField(help_text="小便器数を入力してください")
    # 温水洗浄便座
    warm_water_washing_toilet_seat = models.BooleanField(null=True)
    # チャイルドシート
    child_seat = models.BooleanField(null=True)
    # おむつ交換設備
    child_facility = models.BooleanField(null=True)
    # バリアフリートイレ
    barrier_free_toilet = models.BooleanField(null=True)
    # 車いす対応
    wheelchair = models.BooleanField(null=True)
    # パウダールーム
    powder_room = models.BooleanField(null=True)
    # 姿見
    full_length_mirror = models.BooleanField(null=True)
    # フィッティングボード
    fitting_board = models.BooleanField(null=True)
    # ゴミ箱
    trash_can = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.toilet_id.place}({self.toilet_id.station_id.station_name})"

    def warm_water_washing_toilet_seat_display(self):
        """温水洗浄便座の〇☓表示"""
        if self.warm_water_washing_toilet_seat is None:
            return "-"
        return "〇" if self.warm_water_washing_toilet_seat else "☓"

    def child_facility_display(self):
        """おむつ交換設備の〇☓表示"""
        if self.child_facility is None:
            return "-"
        return "〇" if self.child_facility else "☓"

    def barrier_free_toilet_display(self):
        """バリアフリートイレの〇☓表示"""
        if self.barrier_free_toilet is None:
            return "-"
        return "〇" if self.barrier_free_toilet else "☓"

    def wheelchair_display(self):
        """車いす対応の〇☓表示"""
        if self.wheelchair is None:
            return "-"
        return "〇" if self.wheelchair else "☓"
    
    def full_length_mirror_display(self):
        """姿見の〇☓表示"""
        if self.full_length_mirror is None:
            return "-"
        return "〇" if self.full_length_mirror else "☓"
    
    def fitting_board_display(self):
        """フィッティングボードの〇☓表示"""
        if self.fitting_board is None:
            return "-"
        return "〇" if self.fitting_board else "☓"
    
    def trash_can_display(self):
        """ゴミ箱の〇☓表示"""
        if self.trash_can is None:
            return "-"
        return "〇" if self.trash_can else "☓"
    
    def powder_room_display(self):
        """パウダールームの〇☓表示"""
        if self.powder_room is None:
            return "-"
        return "〇" if self.powder_room else "☓"
    
    def child_seat_display(self):
        """チャイルドシートの〇☓表示"""
        if self.child_seat is None:
            return "-"
        return "〇" if self.child_seat else "☓"


class FemaleToilet(models.Model):
    """女性用トイレテーブル"""

    toilet_id = models.ForeignKey(ToiletMaster, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    # 初期データ(きれいさ)
    initial_value = models.FloatField(null=True)
    # 初期データ(広さ)
    initial_size = models.FloatField(null=True)
    # 初期データ(きれいさ)
    initial_congestion = models.FloatField(null=True)
    # きれいさ(平均値:随時更新)
    value = models.FloatField(null=True)
    # 広さ(平均値:随時更新)
    size = models.FloatField(null=True)
    # 空き具合(平均値:随時更新)
    congestion = models.FloatField(null=True)
    # 温水洗浄便座
    warm_water_washing_toilet_seat = models.BooleanField(null=True)
    # チャイルドシート
    child_seat = models.BooleanField(null=True)
    # おむつ交換設備
    child_facility = models.BooleanField(null=True)
    # バリアフリートイレ
    barrier_free_toilet = models.BooleanField(null=True)
    # 車いす対応
    wheelchair = models.BooleanField(null=True)
    # パウダールーム
    powder_room = models.BooleanField(null=True)
    # 姿見
    full_length_mirror = models.BooleanField(null=True)
    # フィッティングボード
    fitting_board = models.BooleanField(null=True)
    # ゴミ箱
    trash_can = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.toilet_id.place}({self.toilet_id.station_id.station_name})"

    def warm_water_washing_toilet_seat_display(self):
        """温水洗浄便座の〇☓表示"""
        if self.warm_water_washing_toilet_seat is None:
            return "-"
        return "〇" if self.warm_water_washing_toilet_seat else "☓"

    def child_facility_display(self):
        """おむつ交換設備の〇☓表示"""
        if self.child_facility is None:
            return "-"
        return "〇" if self.child_facility else "☓"

    def barrier_free_toilet_display(self):
        """バリアフリートイレの〇☓表示"""
        if self.barrier_free_toilet is None:
            return "-"
        return "〇" if self.barrier_free_toilet else "☓"

    def wheelchair_display(self):
        """車いす対応の〇☓表示"""
        if self.wheelchair is None:
            return "-"
        return "〇" if self.wheelchair else "☓"

    def powder_room_display(self):
        """パウダールームの〇☓表示"""
        if self.powder_room is None:
            return "-"
        return "〇" if self.powder_room else "☓"
    
    def full_length_mirror_display(self):
        """姿見の〇☓表示"""
        if self.full_length_mirror is None:
            return "-"
        return "〇" if self.full_length_mirror else "☓"
    
    def fitting_board_display(self):
        """フィッティングボードの〇☓表示"""
        if self.fitting_board is None:
            return "-"
        return "〇" if self.fitting_board else "☓"
    
    def trash_can_display(self):
        """ゴミ箱の〇☓表示"""
        if self.trash_can is None:
            return "-"
        return "〇" if self.trash_can else "☓"
    
    def child_seat_display(self):
        """チャイルドシートの〇☓表示"""
        if self.child_seat is None:
            return "-"
        return "〇" if self.child_seat else "☓"


class MultiFunctionalToilet(models.Model):
    """多機能トイレテーブル"""

    toilet_id = models.ForeignKey(ToiletMaster, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    # 初期データ(きれいさ)
    initial_value = models.FloatField(null=True)
    # 初期データ(広さ)
    initial_size = models.FloatField(null=True)
    # 初期データ(きれいさ)
    initial_congestion = models.FloatField(null=True)
    # きれいさ(平均値:随時更新)
    value = models.FloatField(null=True)
    # 広さ(平均値:随時更新)
    size = models.FloatField(null=True)
    # 空き具合(平均値:随時更新)
    congestion = models.FloatField(null=True)
    # 温水洗浄便座
    warm_water_washing_toilet_seat = models.BooleanField(null=True)
    # チャイルドシート
    child_seat = models.BooleanField(null=True)
    # おむつ交換設備
    child_facility = models.BooleanField(null=True)
    # バリアフリートイレ
    barrier_free_toilet = models.BooleanField(null=True)
    # 車いす対応
    wheelchair = models.BooleanField(null=True)
    # 姿見
    full_length_mirror = models.BooleanField(null=True)
    # フィッティングボード
    fitting_board = models.BooleanField(null=True)
    # ゴミ箱
    trash_can = models.BooleanField(null=True)

    def __str__(self):
        return f"{self.toilet_id.place}({self.toilet_id.station_id.station_name})"

    def warm_water_washing_toilet_seat_display(self):
        """温水洗浄便座の〇☓表示"""
        if self.warm_water_washing_toilet_seat is None:
            return "-"
        return "〇" if self.warm_water_washing_toilet_seat else "☓"

    def child_facility_display(self):
        """おむつ交換設備の〇☓表示"""
        if self.child_facility is None:
            return "-"
        return "〇" if self.child_facility else "☓"

    def barrier_free_toilet_display(self):
        """バリアフリートイレの〇☓表示"""
        if self.barrier_free_toilet is None:
            return "-"
        return "〇" if self.barrier_free_toilet else "☓"

    def wheelchair_display(self):
        """車いす対応の〇☓表示"""
        if self.wheelchair is None:
            return "-"
        return "〇" if self.wheelchair else "☓"
    
    def full_length_mirror_display(self):
        """姿見の〇☓表示"""
        if self.full_length_mirror is None:
            return "-"
        return "〇" if self.full_length_mirror else "☓"
    
    def fitting_board_display(self):
        """フィッティングボードの〇☓表示"""
        if self.fitting_board is None:
            return "-"
        return "〇" if self.fitting_board else "☓"
    
    def trash_can_display(self):
        """ゴミ箱の〇☓表示"""
        if self.trash_can is None:
            return "-"
        return "〇" if self.trash_can else "☓"
    
    def child_seat_display(self):
        """チャイルドシートの〇☓表示"""
        if self.child_seat is None:
            return "-"
        return "〇" if self.child_seat else "☓"
    
class ToiletStall(models.Model):
    male_toilet_id = models.ForeignKey(MaleToilet, on_delete=models.SET_NULL, null=True, blank=True)
    female_toilet_id = models.ForeignKey(FemaleToilet, on_delete=models.SET_NULL, null=True, blank=True)
    multi_toilet_id = models.ForeignKey(MultiFunctionalToilet, on_delete=models.SET_NULL, null=True, blank=True)
    western_style = models.IntegerField(blank=True, null=True)
    japanese_style = models.IntegerField(blank=True, null=True)

    def clean(self):
        # 登録フィールドを制御する
        related_fields = [self.male_toilet_id, self.female_toilet_id, self.multi_toilet_id]
        filled = [field for field in related_fields if field is not None]

        if len(filled) == 0:
            raise ValidationError("男性、女性、多機能トイレのどれかのIDを入力してください")
        elif len(filled) > 1:
            raise ValidationError("男性、女性、多機能トイレのいずれか1つのみ登録ができます")

class MaleToiletComments(models.Model):
    """男性トイレコメントテーブル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=300)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    value = models.IntegerField(help_text="5段階で数値を入力してください")
    size = models.IntegerField(help_text="5段階で数値を入力してください", null=True)
    congestion = models.IntegerField(help_text="5段階で数値を入力してください", null=True)
    toilet = models.ForeignKey(MaleToilet, on_delete=models.CASCADE)
    data_create = models.DateTimeField(
        default=timezone.now,
        help_text="コメントされた日時"
    )

class FemaleToiletComments(models.Model):
    """女性トイレコメントテーブル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=300)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    value = models.IntegerField(help_text="5段階で数値を入力してください")
    size = models.IntegerField(help_text="5段階で数値を入力してください", null=True)
    congestion = models.IntegerField(help_text="5段階で数値を入力してください", null=True)
    toilet = models.ForeignKey(FemaleToilet, on_delete=models.CASCADE)
    data_create = models.DateTimeField(
        default=timezone.now,
        help_text="コメントされた日時"
    )

class MultifunctionalToiletComments(models.Model):
    """多機能トイレコメントテーブル"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=300)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    value = models.IntegerField(help_text="5段階で数値を入力してください")
    size = models.IntegerField(help_text="5段階で数値を入力してください", null=True)
    congestion = models.IntegerField(help_text="5段階で数値を入力してください", null=True)
    toilet = models.ForeignKey(MultiFunctionalToilet, on_delete=models.CASCADE)
    data_create = models.DateTimeField(
        default=timezone.now,
        help_text="コメントされた日時"
    )
