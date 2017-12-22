from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import pytz


class MainStream(models.Model):
    url = models.URLField(verbose_name='URL потока', null=False, blank=False)
    volume = models.PositiveSmallIntegerField(verbose_name='Громкость', validators=[MaxValueValidator(100)] ,default=50, null=True)
    description = models.TextField(verbose_name='Название потока', max_length=255, null=True, blank=True)

    class Meta():
        verbose_name = "Основной поток"
        verbose_name_plural = "Основные потоки"

    def __str__(self):
        return "{}, {}".format(self.description, self.url)

class Inserts(models.Model):
    description = models.CharField(verbose_name='Название рекламной вставки', max_length=255, null=True, blank=True)
    url = models.URLField(verbose_name='URL потока', null=False, blank=False)
    time = models.TimeField(verbose_name="Время начала", null=False, blank=False)
    volume = models.PositiveSmallIntegerField(verbose_name='Громкость', validators=[MaxValueValidator(100)], default=50, null=True)

    class Meta():
        verbose_name = "Рекламные вставка"
        verbose_name_plural = "Рекламные вставки"

    def __str__(self):
        return "{}, {}".format(self.description, self.time)


class Silent(models.Model):
    description = models.TextField(verbose_name='Описание', max_length=255, null=False, blank=False)
    time_start = models.TimeField(verbose_name="Начало тихой зоны", null=False, blank=False)
    time_end = models.TimeField(verbose_name="Конец тихой зоны", null=False, blank=False)

    class Meta():
        verbose_name = "Зона тишины"
        verbose_name_plural = "Зоны тишины"

    def __str__(self):
        return "{}, {} - {}".format(self.description, self.time_start, self.time_end)


class Schedule(models.Model):
    title = models.CharField(verbose_name='Название расписания', max_length=255, null=False, blank=False)
    change_time = models.DateTimeField(verbose_name="Последнее изменение", auto_now=True)
    main_stream = models.ForeignKey(MainStream, verbose_name='Главный поток', related_name='main_stream')
    inserts = models.ManyToManyField(Inserts, verbose_name='Рекламные вставки', related_name='inserts', blank=True)
    silent = models.ManyToManyField(Silent, verbose_name='Зоны тишины', related_name='silent', blank=True)

    class Meta():
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

    def get_inserts_count(self):
        ins = self.inserts.count()
        if ins:
            return 'Рекламных вставок: {}'.format(ins)
        else:
            return 'Рекламных вставок нет'
    get_inserts_count.short_description = 'Рекламные вставки'

    def get_silent_count(self):
        silent = self.silent.count()
        if silent:
            return 'Зон тишины: {}'.format(silent)
        else:
            return 'Зон тишины НЕТ'
    get_silent_count.short_description = 'Зоны тишины'

    def __str__(self):
        return "{}. *{}*".format(self.title, self.change_time.strftime('%Y-%m-%d %H:%M:%S'))


class Player(models.Model):
    player_id = models.CharField(verbose_name='ID плеера', help_text='Уникальное значение, не более 10 символов', unique=True, max_length=10, null=False, blank=False)
    title = models.CharField(verbose_name='Описание', max_length=255, null=False, blank=False)
    address = models.CharField('Адрес установки', max_length=100,)
    schedule = models.ForeignKey(Schedule, verbose_name='Расписание', null=True, blank=True)
    update_granted = models.BooleanField("Разрешено обновление ПЛЕЕРА", null=False, blank=True, default=False)
    send_updater = models.BooleanField("Отправить АПДЕЙТЕР", null=False, blank=True, default=False)

    class Meta():
        verbose_name = "Плееры"
        verbose_name_plural = "Плееры"

    def __str__(self):
        return "{} {}".format(self.player_id, self.title)

    def stat(self):
        st = self.status
        return '\'{}\' на {}'.format(st.get_status_display(), (st.timestamp+datetime.timedelta(hours=2)).strftime('%d-%m-%Y %H:%M:%S'))
    stat.short_description = 'Статус плеера'




class PlayerStatus(models.Model):

    STATUS_TYPE = (
        (None, 'Нет полученного статуса'),
        (0, 'ОК'),
        (1, 'Нет текущего расписания'),
        (2, 'Главный поток закончился'),
        (3, 'Ошибка главного плеера'),
        (4, 'Ошибка рекламного плеера')
    )

    player = models.OneToOneField(Player, verbose_name='Плеер', related_name='status', on_delete=models.CASCADE)
    status = models.PositiveIntegerField(verbose_name='Статус плеера', choices=STATUS_TYPE, default=None, null=True)
    timestamp = models.DateTimeField(verbose_name='Статус на', blank=False, default=datetime.datetime.now())
    current_sch_time = models.DateTimeField(verbose_name='Дата последнего расписания', blank=True, null=True)
    player_version = models.PositiveIntegerField(verbose_name='Версия плеера', blank=True, null=True)
    updater_present = models.BooleanField('Апдейтер в наличии', null=False, blank=True, default=False)

    class Meta():
        verbose_name = "Статус плеера"
        verbose_name_plural = "Статус плеера"

@receiver(post_save, sender=Player)
def create_user_report(sender, instance, created, **kwargs):
    if created:
        PlayerStatus.objects.create(player=instance)


class UpdateFile(models.Model):

    FILE_TYPE = (
        ('updater.py', 'UPDATER'),
        ('api_player.py', 'PLAYER')
    )

    file_type = models.CharField(verbose_name='Тип файла', choices=FILE_TYPE, max_length=20, blank=False, null=False, default=None)
    version = models.PositiveIntegerField(verbose_name='Версия', blank=False, null=False)
    url = models.FileField(verbose_name='URL файла', upload_to='updater')

    class Meta():
        verbose_name = "Update скрипт"
        verbose_name_plural = "Update скрипты"
        get_latest_by = 'version'

    def __str__(self):
        return "{} {}".format(self.version, self.url)