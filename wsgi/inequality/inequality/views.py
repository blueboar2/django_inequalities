#encoding: utf-8

from django.views.decorators.csrf import csrf_protect

from datetime import datetime

import subprocess

import json
from django.http import HttpResponse

from django import forms

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Student, Tests, TestsAssign, TestsStats

def student_check(user):
    return Student.objects.filter(id = user.id).first()

@user_passes_test(student_check)
def tests(request):
    ourtests = TestsAssign.objects.filter(studentnumber__id = request.user.id).values('id', 'testnumber', 'completequestions', 'truequestions')
    totemplate = []
    for otest in ourtests :
        testname = Tests.objects.filter(id = otest['testnumber']).values('testname', 'testnumquestions')
        if (otest['completequestions'] == None):
           otest['completequestions'] = 0
        if (otest['truequestions'] == None):
           otest['truequestions'] = 0
        totemplate.append({'id' : otest['id'], 'testname' : testname[0]['testname'], 'testnumquestions' : testname[0]['testnumquestions'], 'completequestions' : otest['completequestions'], 'truequestions' : otest['truequestions'] })
    return render_to_response ('../templates/tests.html', { "tests": totemplate })

def runtest(request, testassignnum = 0):
    tes = TestsAssign.objects.filter(id = testassignnum).first()
    if (tes == None):
     tohandle = 0
     return render_to_response ('../templates/test.html', { "tohandle": tohandle })
    elif (tes.studentnumber.id != request.user.id):
     tohandle = 1
     return render_to_response ('../templates/test.html', { "tohandle": tohandle })
    else:
     answered = tes.completequestions
     if (answered == None):
      answered = 0
     testnum = tes.testnumber.id
     questions = Tests.objects.filter(id = testnum).values('testnumquestions')[0]['testnumquestions']
     if (questions == answered):
      return tests(request)
     else:
      tohandle = 2
      questiontext = TestsStats.objects.filter(assignedtest = testassignnum).filter(questionnumber = answered + 1).values('question')[0]['question']
      return render_to_response ('../templates/test.html', { "tohandle": tohandle, "questiontext": questiontext, "numquestion": answered + 1, "questions": questions, "testassignnum": testassignnum }, context_instance=RequestContext(request))

class TryToGuessForm(forms.Form):
    mathjaxanswer = forms.CharField(label=u'Ответ на неравенство', max_length=100)
    testassignnum = forms.IntegerField(label=u'Номер назначения теста')
    numquestion = forms.IntegerField(label=u'Номер вопроса')

def trytoanswer(request):
      data = {}
      form = TryToGuessForm(request.POST)
      if form.is_valid():
        xcleaned_data = form.cleaned_data['mathjaxanswer']
        xcleaned_data = xcleaned_data.replace('uuu', 'U')
        xcleaned_data = xcleaned_data.replace('uu', 'U')
        xcleaned_data = xcleaned_data.replace('nnn', '^')
        xcleaned_data = xcleaned_data.replace('nn', '^')

        cmd = ["/var/www/localhost/htdocs/static/interval/interval", xcleaned_data, xcleaned_data]
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.communicate()
        retline = ret[0].rstrip()
        if (retline[-9:] == 'IDENTICAL'):
            testassignnum = form.cleaned_data['testassignnum']
            numquestion = form.cleaned_data['numquestion']
            rightanswer = TestsStats.objects.filter(assignedtest__id = testassignnum).filter(questionnumber = numquestion).values('answer')[0]['answer']
            cmd = ["/var/www/localhost/htdocs/static/interval/interval", xcleaned_data, rightanswer]
            p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ret = p.communicate()
            retline = ret[0].rstrip()

            testsstat = TestsStats.objects.filter(assignedtest__id = testassignnum).filter(questionnumber = numquestion).first()
            ourtest = TestsAssign.objects.filter(id = testassignnum).first()
            if (ourtest.truequestions == None):
             ourtest.truequestions = 0
            if (ourtest.completequestions == None):
             ourtest.completequestions = 0
            ourtest.completequestions = ourtest.completequestions + 1

            if (retline[-13:] == 'NOT identical'):
               testsstat.isanswertrue = False
            else:
               testsstat.isanswertrue = True
               ourtest.truequestions = ourtest.truequestions + 1

            data['isok'] = 'OK'		# WRONG, BUT OK
            testsstat.studentanswer = xcleaned_data
            testsstat.save()

            totalquestions = Tests.objects.filter(id = ourtest.testnumber.id).values('testnumquestions')[0]['testnumquestions']

            if (ourtest.completequestions == totalquestions):
               ourtest.completedate = datetime.now()

            ourtest.save()
        else:
            if (p.returncode == 30):
                data['isok'] = u"Ошибка: правая граница интервала меньше левой"
            elif (p.returncode == 40):
                data['isok'] = u"Ошибка: если левая и правая граница интервала равны, интервал должен быть закрытым"
            elif (p.returncode == 10):
                data['isok'] = u"Ошибка: минус бесконечность должна быть в начале интервала, а не в конце"
            elif (p.returncode == 20):
                data['isok'] = u"Ошибка: плюс бесконечность должна быть в конце интервала, а не в начале"
            elif (p.returncode == 50):
                data['isok'] = u"Ошибка: при использовании бесконечностей интервал должен быть открытым, а не закрытым"
            elif (p.returncode == 220):
                data['isok'] = u"Ошибка работы с корнями"
            elif (p.returncode == 1):
                data['isok'] = u"Ошибка разбора выражения"
            elif (p.returncode == 2):
                data['isok'] = u"Ошибка разбора выражения"
            else:
                data['isok'] = u"Неизвестная ошибка"
      return HttpResponse(json.dumps(data), content_type = "application/json")

def assignajax(request):
      value = int(request.POST['value'])
      students = Student.objects.filter(studentgroup = value)
      toout = ""
      for student in students:
         toout = toout + '<option value="' + str(student.id) + '">' + student.first_name + " " + student.last_name + "</option>"
      return HttpResponse(toout)
