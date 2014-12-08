# encoding: utf-8

import subprocess
import random

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from models import Student, Teacher, Student_groups, Inequalities, Tests, TestsAssign, TestsStats

class TeacherChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    def clean_password(self):
        return self.initial["password"]

    class Meta:
        model = Teacher

class TeacherAdmin(UserAdmin):
    form = TeacherChangeForm
    list_display = ('username', 'last_name', 'first_name',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
                'first_name', 'last_name', 'email'
            )}),
        #(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        #(_('Groups'), {'fields': ('groups',)}),
    )

class StudentChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    def clean_password(self):
        return self.initial["password"]

    class Meta:
        model = Student

class StudentAdmin(UserAdmin):
    form = StudentChangeForm
    list_display = ('username', 'last_name', 'first_name',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
                'first_name', 'last_name', 'email', 'studentgroup',
            )}),
        #(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        #(_('Groups'), {'fields': ('groups',)}),
    )

class Student_groupsAdmin(admin.ModelAdmin):
    list_display = ('groupnumber',)

class InequalitiesForm(forms.ModelForm):
    inequalityquestion = forms.CharField(label='Задание', max_length=500, widget=forms.Textarea(attrs={'id': 'mathjaxquestion', 'onkeyup': 'updatemathjaxquestion()'}))
    inequalityanswer = forms.CharField(label='Ответ на задание', max_length=500, widget=forms.Textarea(attrs={'id': 'mathjaxanswer', 'onkeyup': 'updatemathjaxanswer()'}))

    class Meta:
       model = Inequalities

    def clean(self):
        cleaned_data = super(InequalitiesForm, self).clean()
        inequalityteacher = Teacher.objects.filter(id = self.current_user.id).first()
        if (inequalityteacher == None):
          raise forms.ValidationError("Вы не можете добавить неравенство, так как вы не преподаватель")
        else:
          return self.cleaned_data

    def clean_inequalityanswer(self):
	cleaned_data = self.cleaned_data['inequalityanswer']
	xcleaned_data = cleaned_data.replace('uuu', 'U')
	xcleaned_data = xcleaned_data.replace('uu', 'U')
	xcleaned_data = xcleaned_data.replace('nnn', '^')
	xcleaned_data = xcleaned_data.replace('nn', '^')
	cmd = ["/var/www/localhost/htdocs/static/interval/interval", xcleaned_data, xcleaned_data]
	p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	ret = p.communicate()
	retline = ret[0].rstrip()
	if (retline[-9:] == 'IDENTICAL'):
	    return cleaned_data
	else:
	    if (p.returncode == 30):
		raise forms.ValidationError("Ошибка: правая граница интервала меньше левой")
	    elif (p.returncode == 40):
		raise forms.ValidationError("Ошибка: если левая и правая граница интервала равны, интервал должен быть закрытым")
	    elif (p.returncode == 10):
		raise forms.ValidationError("Ошибка: минус бесконечность должна быть в начале интервала, а не в конце")
	    elif (p.returncode == 20):
		raise forms.ValidationError("Ошибка: плюс бесконечность должна быть в конце интервала, а не в начале")
	    elif (p.returncode == 50):
		raise forms.ValidationError("Ошибка: при использовании бесконечностей интервал должен быть открытым, а не закрытым")
	    elif (p.returncode == 220):
		raise forms.ValidationError("Ошибка работы с корнями")
	    elif (p.returncode == 1):
		raise forms.ValidationError("Ошибка разбора выражения")
	    elif (p.returncode == 2):
		raise forms.ValidationError("Ошибка разбора выражения")
	    else:
		raise forms.ValidationError("%s" % p.returncode)

class InequalitiesAdmin(admin.ModelAdmin):
    form = InequalitiesForm

    list_display = ('inequalityquestion', 'inequalityanswer')
    fields = ('inequalityquestion', 'inequalityanswer')

    class Media:
        js = ('/static/mathjax/MathJax.js?config=AM_HTMLorMML-full',
              '/static/mathjax/reload.js',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "inequalitygroup":
            kwargs["queryset"] = Tests.objects.filter(testteacher = Teacher.objects.get(id = request.user.id))
        return super(InequalitiesAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj = None, **kwargs):
         form = super(InequalitiesAdmin, self).get_form(request, **kwargs)
         form.current_user = request.user
         return form

    def save_model(self, request, obj, form, change):
        obj.inequalityteacher = Teacher.objects.get(id = request.user.id)
        obj.save()

    def queryset(self, request):
      testteacher = Teacher.objects.filter(id = request.user.id).first()
      if (testteacher == None):
        return Inequalities.objects.all()
      else:
        return Inequalities.objects.filter(inequalityteacher = Teacher.objects.get(id = request.user.id))


class TestsAdminForm(forms.ModelForm):
    class Meta:
        model = Tests

    def clean(self):
      if (self.instance.pk != None):
           raise forms.ValidationError("Нельзя менять тест после его создания")
      else:
        cleaned_data = super(TestsAdminForm, self).clean()
        if ('testnumquestions' in cleaned_data):
         testteacher = Teacher.objects.filter(id = self.current_user.id).first()
         if (testteacher == None):
           raise forms.ValidationError("Вы не можете добавить тест, так как вы не преподаватель")
         else:
             if (cleaned_data['testnumquestions']>len(cleaned_data['testinequalities'])):
               raise forms.ValidationError("В тесте не может быть больше вопросов чем неравенств")
             else:
               if (cleaned_data['testnumquestions']<=0):
                 raise forms.ValidationError("В тесте должно быть положительное число вопросов")
               else:
                 return self.cleaned_data
        else:
          return self.cleaned_data	#Will be error in IntegerField

class TestsAdmin(admin.ModelAdmin):
    list_display = ('testname','testnumquestions',)
    fields = ('testname','testinequalities','testnumquestions',)
    form = TestsAdminForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
      testteacher = Teacher.objects.filter(id = request.user.id).first()
      if (testteacher == None):
        queryset_ = Inequalities.objects.all()
      else:
        queryset_ = Inequalities.objects.filter(inequalityteacher = Teacher.objects.get(id = request.user.id))

      if db_field.name == "testinequalities":
        kwargs["queryset"] = queryset_
      return super(TestsAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj = None, **kwargs):
         form = super(TestsAdmin, self).get_form(request, **kwargs)
         form.current_user = request.user
         return form

    def save_model(self, request, obj, form, change):
        obj.testteacher = Teacher.objects.get(id = request.user.id)
        obj.save()

    def queryset(self, request):
      testteacher = Teacher.objects.filter(id = request.user.id).first()
      if (testteacher == None):
        return Tests.objects.all()
      return Tests.objects.filter(testteacher = Teacher.objects.get(id = request.user.id))

class TestsAssignForm(forms.ModelForm):
    studentgroup = forms.ModelChoiceField(label='Группа студентов', queryset=Student_groups.objects.all(), widget=forms.Select(attrs={'onchange': 'updatestudents()'}))
    studentsingroup = forms.ModelMultipleChoiceField(label='Студенты в группе', queryset=Student.objects.all())

    def save(self, commit = True):
     fisn = self.cleaned_data.get('studentsingroup', None).first()
     sting = self.cleaned_data.get('studentsingroup', None)
     tnum = self.cleaned_data.get('testnumber', None)
     for sig in sting:
       if (fisn.id != sig.id):
        newobj = TestsAssign(studentnumber=sig, testnumber = tnum, completedate = None, completequestions = None, truequestions = None,)
        result = newobj.save()
     obj = super(TestsAssignForm, self).save(commit=False)
     obj.studentnumber = self.cleaned_data.get('studentsingroup', None).first()
     if commit:
      obj.save()
     return obj

    class Meta:
        model = TestsAssign

class TestsAssignAdmin(admin.ModelAdmin):
    list_display = ('testnumber', 'studentnumber','assigndate', 'completedate','completequestions','truequestions',)
    fields = ('testnumber', 'studentgroup', 'studentsingroup',)
    form = TestsAssignForm

    class Media:
        js = ('/static/js/assign.js',)

    def queryset(self, request):
      testteacherx = Teacher.objects.filter(id = request.user.id).first()
      if (testteacherx == None):
        return TestsAssign.objects.all()
      else:
        testsx = Tests.objects.filter(testteacher = testteacherx).first()
        if (testsx == None):
          return TestsAssign.objects.none()
        else:
          return TestsAssign.objects.filter(testnumber = Tests.objects.filter(testteacher = testteacherx))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
      testteacher = Teacher.objects.filter(id = request.user.id).first()
      if (testteacher == None):
        queryset_ = Tests.objects.all()
      else:
        queryset_ = Tests.objects.filter(testteacher = Teacher.objects.get(id = request.user.id))

      if db_field.name == "testnumber":
        kwargs["queryset"] = queryset_
      return super(TestsAssignAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class TestsStatsForm(forms.ModelForm):

    def clean(self):
       raise forms.ValidationError("Нельзя менять статистику тестов")

    class Meta:
        model = TestsStats

class TestsStatsAdmin(admin.ModelAdmin):
    list_display = ('get_current_test','get_current_student', 'get_current_group', 'get_assign_date', 'questionnumber','question','answer','studentanswer','isanswertrue',)
    fields = ('questionnumber','question','answer','studentanswer','isanswertrue',)
    list_filter = ('assignedtest__testnumber__testname','assignedtest__studentnumber','assignedtest__studentnumber__studentgroup', 'assignedtest__assigndate', 'isanswertrue')
    form = TestsStatsForm

    def queryset(self, request):
      testteacherx = Teacher.objects.filter(id = request.user.id).first()
      if (testteacherx == None):
        return TestsStats.objects.all()
      else:
        testsx = Tests.objects.filter(testteacher = testteacherx).first()
        if (testsx == None):
          return TestsStats.objects.none()
        else:
          assignx = TestsAssign.objects.filter(testnumber = Tests.objects.filter(testteacher = testteacherx)).first()
          if (assignx == None):
            return TestsStats.objects.none()
          else:
            return TestsStats.objects.filter(assignedtest = TestsAssign.objects.filter(testnumber = Tests.objects.filter(testteacher = testteacherx)))


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Student_groups, Student_groupsAdmin)
admin.site.register(Inequalities, InequalitiesAdmin)
admin.site.register(Tests, TestsAdmin)
admin.site.register(TestsAssign, TestsAssignAdmin)
admin.site.register(TestsStats, TestsStatsAdmin)


#######################################################################

@receiver(post_save, sender = Teacher)
def add_to_teacher_group_post(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name=u'Преподаватели'))

@receiver(post_save, sender = Student)
def add_to_student_group_post(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(Group.objects.get(name=u'Студенты'))

@receiver(post_save, sender = TestsAssign)
def add_to_table_testsstats(sender, instance, created, **kwargs):
    if (created == True):
      random.seed()
      numquestions = instance.testnumber.testnumquestions
      ourtest = instance.testnumber
      allinequalities = list(ourtest.testinequalities.all())
      alllength = len(allinequalities)
      questionlist = random.sample(xrange(0, alllength), numquestions)

      for question in xrange(0, numquestions):
        testsstat = TestsStats();
        testsstat.assignedtest = instance
        testsstat.questionnumber = question+1
        ourinequalities = Inequalities.objects.filter(id = allinequalities[questionlist[question]].id).first()
        testsstat.question = ourinequalities.inequalityquestion
        testsstat.answer = ourinequalities.inequalityanswer
        testsstat.studentanswer = None
        testsstat.isanswertrue = False
        testsstat.save()
