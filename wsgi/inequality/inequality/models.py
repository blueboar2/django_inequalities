# encoding: utf-8

from pprint import pprint

from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

###########################################################################################################
################################################# TEACHER #################################################
###########################################################################################################

class Teacher(User):
    otchestvo = models.CharField(u'Отчество', max_length=30)

    class Meta:
        verbose_name = u'Преподаватель'
        verbose_name_plural = u'Преподаватели'

    def save(self, *args, **kwargs):
        self.is_active = True
        self.is_staff = True
        self.is_superuser = False
        super(Teacher, self).save(*args, **kwargs)
    pass

    def __unicode__(self):
       return self.first_name + " " + self.last_name + " " + self.otchestvo

###########################################################################################################
######################################### STUDENT_GROUPS  #################################################
###########################################################################################################

class Student_groups(models.Model):
    groupnumber = models.CharField(u'Номер группы', max_length=15)

    def __unicode__(self):
       return self.groupnumber

    class Meta:
        verbose_name = u'Группа студентов'
        verbose_name_plural = u'Группы студентов'

###########################################################################################################
############################################# STUDENT #####################################################
###########################################################################################################

class Student(User):
    otchestvo = models.CharField(u'Отчество', max_length=30)
    studentgroup = models.ForeignKey(Student_groups, verbose_name=u'Группа студента', null=True)

    class Meta:
        verbose_name = u'Студент'
        verbose_name_plural = u'Студенты'

    def save(self, *args, **kwargs):
        self.is_active = True
        self.is_staff = False
        self.is_superuser = False
        super(Student, self).save(*args, **kwargs)
    pass

    def __unicode__(self):
       return self.first_name + " " + self.last_name + " " + self.otchestvo

###########################################################################################################
########################################## INEQUALITIES ###################################################
###########################################################################################################

class Inequalities(models.Model):
    inequalityteacher = models.ForeignKey(Teacher, verbose_name=u'Преподаватель')
    inequalityquestion = models.CharField(u'Задание', max_length=500)
    inequalityanswer = models.CharField(u'Ответ на задание', max_length=500)

    class Meta:
        verbose_name = u'Неравенство'
        verbose_name_plural = u'Неравенства'

    def __unicode__(self):
       return u'Неравенство '+str(self.inequalityquestion)

###########################################################################################################
############################################# TESTS #######################################################
###########################################################################################################

class Tests(models.Model):
    testteacher = models.ForeignKey(Teacher, verbose_name=u'Преподаватель')
    testname = models.CharField(u'Название теста', max_length=100)
    testinequalities = models.ManyToManyField(Inequalities, verbose_name=u'Входящие в тест неравенства')
    testnumquestions = models.IntegerField(u'Число вопросов в тесте')

    def __unicode__(self):
       return self.testname

    class Meta:
        verbose_name = u'Тест'
        verbose_name_plural = u'Тесты'

###########################################################################################################
########################################### TESTS_ASSIGN ##################################################
###########################################################################################################

class TestsAssign(models.Model):
    testnumber = models.ForeignKey(Tests, verbose_name=u'Тест')
    studentnumber = models.ForeignKey(Student, verbose_name=u'Студент')
    assigndate = models.DateTimeField(verbose_name=u'Дата назначения теста', auto_now_add=True)
    completedate = models.DateTimeField(verbose_name=u'Дата сдачи теста', null = True)
    completequestions = models.IntegerField(u'Число отвеченных вопросов', null = True)
    truequestions = models.IntegerField(u'Число верных ответов', null = True)

    def __unicode__(self):
       return u'Назначение теста ' + self.testnumber.testname + u' для студента ' + self.studentnumber.first_name + ' ' + self.studentnumber.last_name + ' ' + self.studentnumber.otchestvo

    class Meta:
        verbose_name = u'Назначение теста '
        verbose_name_plural = u'Назначения тестов '

###########################################################################################################
########################################### TESTS_STATS ###################################################
###########################################################################################################

class TestsStats(models.Model):
    assignedtest = models.ForeignKey(TestsAssign, verbose_name=u'Назначенный тест')
    questionnumber = models.IntegerField(u'Номер вопроса')
    question = models.CharField(u'Задание', max_length=500)
    answer = models.CharField(u'Верный ответ на задание', max_length=500)
    studentanswer = models.CharField(u'Ответ на задание данный студентом', max_length=500, null = True)
    isanswertrue = models.BooleanField(u'Верный ли ответ')

    def __unicode__(self):
       return u'Статистика теста ' + self.assignedtest.testnumber.testname + u' для студента ' + self.assignedtest.studentnumber.first_name + ' ' + self.assignedtest.studentnumber.last_name + ' ' + self.assignedtest.studentnumber.otchestvo + u', вопрос номер ' + str(self.questionnumber)

    def get_current_test(self):
       tao = TestsAssign.objects.filter(id = self.assignedtest.id).first()
       return Tests.objects.filter(id = tao.testnumber.id).first().testname

    get_current_test.short_description = u'Название теста'

    def get_current_student(self):
       tao = TestsAssign.objects.filter(id = self.assignedtest.id).first()
       stud = Student.objects.filter(id = tao.studentnumber.id).first()
       return stud.first_name + " " + stud.last_name + " " + stud.otchestvo

    get_current_student.short_description = u'Студент'

    def get_current_group(self):
       tao = TestsAssign.objects.filter(id = self.assignedtest.id).first()
       stud = Student.objects.filter(id = tao.studentnumber.id).first()
       group = Student_groups.objects.filter(id = stud.studentgroup.id).first()
       return group.groupnumber

    get_current_group.short_description = u'Группа'

    def get_assign_date(self):
       tao = TestsAssign.objects.filter(id = self.assignedtest.id).first()
       return tao.assigndate

    get_assign_date.short_description = u'Дата назначения'

    class Meta:
        verbose_name = u'Статистика теста '
        verbose_name_plural = u'Статистика по тестам '

###########################################################################################################
###########################################################################################################
###########################################################################################################
