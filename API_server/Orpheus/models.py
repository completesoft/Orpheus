from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


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
        return "{}, {}".format(self.description, self.url)


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


class Location(models.Model):
    title = models.CharField(verbose_name='Название объекта', max_length=255, null=False, blank=False)
    address = models.CharField('Адрес', max_length=100, default='None')
    schedule = models.ForeignKey(Schedule, verbose_name='Расписание', null=True, blank=True)

    class Meta():
        verbose_name = "Локация (e.g. магазин)"
        verbose_name_plural = "Локации"

    def __str__(self):
        return "{} {}".format(self.title, self.schedule)