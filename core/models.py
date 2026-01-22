
from django.db import models

class Equipe(models.Model):
    id_equipe = models.AutoField(db_column='IdEquipe', primary_key=True)
    nome = models.CharField(db_column='Nome', max_length=200)

    class Meta:
        managed = False
        db_table = 'Equipe'
        verbose_name = 'Équipe'
        verbose_name_plural = 'Équipes'

    def __str__(self): return self.nome

class Consultor(models.Model):
    id_consultor = models.AutoField(db_column='IdConsultor', primary_key=True)
    nome = models.CharField(db_column='Nome', max_length=200)
    id_equipe = models.ForeignKey(Equipe, models.DO_NOTHING, db_column='IdEquipe', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Consultor'
        verbose_name = 'Consultor'
        verbose_name_plural = 'Consultores'

    def __str__(self): return self.nome

class Projeto(models.Model):
    id_projeto = models.AutoField(db_column='IdProjeto', primary_key=True)
    nome = models.CharField(db_column='Nome', max_length=200)

    class Meta:
        managed = False
        db_table = 'Projeto'
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'

    def __str__(self): return self.nome

class CapacidadeSemanal(models.Model):
    id_capacidade = models.AutoField(db_column='IdCapacidade', primary_key=True)
    id_consultor = models.ForeignKey(Consultor, models.DO_NOTHING, db_column='IdConsultor')
    data_inicio_semana = models.DateField(db_column='DataInicioSemana')
    dias_disponiveis = models.DecimalField(db_column='DiasDisponiveis', max_digits=5, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'CapacidadeSemanal'
        verbose_name = 'Carga Semanal'
        verbose_name_plural = 'Cargas Semanais'

class CargaSemanalPotencial(models.Model):
    id_carga = models.AutoField(db_column='IdCarga', primary_key=True)
    id_consultor = models.ForeignKey(Consultor, models.DO_NOTHING, db_column='IdConsultor')
    id_projeto = models.ForeignKey(Projeto, models.DO_NOTHING, db_column='IdProjeto')
    data_inicio_semana = models.DateField(db_column='DataInicioSemana')
    tipo = models.CharField(db_column='Tipo', max_length=20, default='Real', editable=False)
    dias = models.DecimalField(db_column='Dias', max_digits=5, decimal_places=0)

    class Meta:
        managed = False
        db_table = 'CargaSemanalPotencial'
        verbose_name = 'Carga Semanal'
        verbose_name_plural = 'Cargas Semanais'
