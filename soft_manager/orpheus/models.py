from django.db import models


class Schedule (models.Model):
    id = models.AutoField(primary_key=True)
    main_stream = models.URLField('Путь к основной музыке')
    main_volume = models.DecimalField('Громкость основной темы', max_digits=2, decimal_places=0)
    description = models.CharField('Описание', max_length=200, default='')
    def __str__(self):
        return 'Расписание %d, %s'%(self.id, self.description)




class Shop (models.Model):
    shop_id = models.IntegerField('Магазин №', unique=True)
    address = models.CharField('Адрес', max_length=100, default='None')
    schedule = models.ForeignKey(Schedule, default=1)
    def __str__(self):
        return 'Магазин №%d, адрес: %s'%(self.shop_id, self.address)
