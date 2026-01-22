
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models
import datetime

# --- Filtres personnalisés ---

class YearListFilter(admin.SimpleListFilter):
    title = _('Ano')
    parameter_name = 'annee'
    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        years = sorted({d.year for d in qs.values_list('data_inicio_semana', flat=True) if d})
        return [(y, str(y)) for y in years]
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(data_inicio_semana__year=int(self.value()))
        return queryset

class MonthListFilter(admin.SimpleListFilter):
    title = _('Mês')
    parameter_name = 'mois'
    def lookups(self, request, model_admin):
        return [(i, datetime.date(2000, i, 1).strftime('%b')) for i in range(1,13)]
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(data_inicio_semana__month=int(self.value()))
        return queryset

class IsoWeekListFilter(admin.SimpleListFilter):
    title = _('Semana')
    parameter_name = 'semaine'
    def lookups(self, request, model_admin):
        # propose 1..53
        return [(i, f"S{i:02d}") for i in range(1,54)]
    def queryset(self, request, queryset):
        if self.value():
            # Django 4.2: use ExtractWeek/ExtractIsoWeek? We'll use iso week via extra or week
            from django.db.models.functions import ExtractWeek
            return queryset.annotate(week=ExtractWeek('data_inicio_semana')).filter(week=int(self.value()))
        return queryset

# --- Admins ---

@admin.register(models.Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('id_equipe','nome')
    search_fields = ('nome',)

@admin.register(models.Consultor)
class ConsultorAdmin(admin.ModelAdmin):
    list_display = ('id_consultor','nome','id_equipe')
    list_filter = ('id_equipe',)
    search_fields = ('nome',)

@admin.register(models.Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('id_projeto','nome')
    search_fields = ('nome',)

@admin.register(models.CargaSemanalPotencial)
class CargaAdmin(admin.ModelAdmin):
    list_display = ('id_carga','id_consultor','id_projeto','data_inicio_semana','tipo','dias')
    list_filter = (YearListFilter, MonthListFilter, IsoWeekListFilter, 'id_consultor','id_projeto','tipo')
    search_fields = ('id_consultor__nome','id_projeto__nome')
    
    
admin.site.site_header = "Lean Way Consulting — Administração"
admin.site.site_title = "Lean Way Consulting"
admin.site.index_title = "Painel de Gestão"

