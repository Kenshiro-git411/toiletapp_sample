from django.contrib import admin
from .models import TrainLine, TrainStation, ToiletMaster, MaleToilet, FemaleToilet, MultiFunctionalToilet, StationTicketGate, ToiletStall, MaleToiletComments, FemaleToiletComments, MultifunctionalToiletComments

class TrainLineAdmin(admin.ModelAdmin):
    list_display = ("id", "train_line_name")
    search_fields = ("train_line_name",)

class TrainStationAdmin(admin.ModelAdmin):
    list_display = ("id", "station_name", "station_name_japanese", "train_line") # 外部キーも表示する
    search_fields = ("station_name",)
    list_filter = ("train_line",) # 路線でフィルタリングする

class ToiletMasterAdmin(admin.ModelAdmin):
    list_display = ("station_id", "place", "station_ticket_gate_id", "open_time", "close_time",)
    search_fields = ("place",)
    list_filter = ("station_id", "station_ticket_gate_id",)

class StationTicketGateAdmin(admin.ModelAdmin):
    list_display = ("station_ticket_gate",)

class ToiletStallAdmin(admin.ModelAdmin):
    list_display = ("male_toilet_id", "female_toilet_id", "multi_toilet_id", "western_style", "japanese_style")

class MaleToiletAdmin(admin.ModelAdmin):
    list_display = ("toilet_id", "initial_value", "initial_size", "initial_congestion", "value", "size", "congestion", "urial", "warm_water_washing_toilet_seat", "child_facility", "barrier_free_toilet", "wheelchair", "powder_room")
    search_fields = ("toilet_id", "value",)
    list_filter = ("toilet_id",)

class FemaleToiletAdmin(admin.ModelAdmin):
    list_display = ("toilet_id", "initial_value", "initial_size", "initial_congestion", "value", "size", "congestion", "warm_water_washing_toilet_seat", "child_facility", "barrier_free_toilet", "wheelchair", "powder_room")
    search_fields = ("toilet_id", "value",)
    list_filter = ("toilet_id",)

class MultiFunctionalToiletAdmin(admin.ModelAdmin):
    list_display = ("toilet_id", "initial_value", "initial_size", "initial_congestion", "value", "size", "congestion","warm_water_washing_toilet_seat", "child_facility", "barrier_free_toilet", "wheelchair",)
    search_fields = ("toilet_id", "value",)
    list_filter = ("toilet_id",)

class MaleToiletCommentsAdmin(admin.ModelAdmin):
    list_display = ("toilet", "user", "gender", "value")
    search_fields = ("toilet", "user", "gender", "value")
    list_filter = ("toilet", "user", "gender", "value")

class FemaleToiletCommentsAdmin(admin.ModelAdmin):
    list_display = ("toilet", "user", "gender", "value")
    search_fields = ("toilet", "user", "gender", "value")
    list_filter = ("toilet", "user", "gender", "value")

class MultifunctionalToiletCommentsAdmin(admin.ModelAdmin):
    list_display = ("toilet", "user", "gender", "value")
    search_fields = ("toilet", "user", "gender", "value")
    list_filter = ("toilet", "user", "gender", "value")


admin.site.register(TrainLine, TrainLineAdmin)
admin.site.register(TrainStation, TrainStationAdmin)
admin.site.register(ToiletMaster, ToiletMasterAdmin)
admin.site.register(StationTicketGate, StationTicketGateAdmin)
admin.site.register(ToiletStall, ToiletStallAdmin)
admin.site.register(MaleToilet, MaleToiletAdmin)
admin.site.register(FemaleToilet, FemaleToiletAdmin)
admin.site.register(MultiFunctionalToilet, MultiFunctionalToiletAdmin)
admin.site.register(MaleToiletComments, MaleToiletCommentsAdmin)
admin.site.register(FemaleToiletComments, FemaleToiletCommentsAdmin)
admin.site.register(MultifunctionalToiletComments, MultifunctionalToiletCommentsAdmin)