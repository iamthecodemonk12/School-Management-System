from PIL import Image

from datetime import date

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

_is_neg = lambda x: x<0

_join = lambda *a: ' '.join([str(i) for i in a])

def fill_zeros(num, digits=3):
    '''Fill number with preceeding zeroes eg. 003 '''
    serial_number = str(num)
    zeros = (digits - len(serial_number))
    zeros = '0' * zeros if not _is_neg(zeros) else ''
    return zeros + serial_number


class Student(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    gender_choices = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    gender_choices_dict = dict(gender_choices)

    first_name = models.CharField(_("student name"), max_length=50, help_text=_("Name of student"))
    last_name = models.CharField(_("last name"), max_length=50, help_text=_("Surname of student"), null=True, blank=True)
    middle_name = models.CharField(_("middle name"), max_length=50, help_text=_("Other name"), null=True, blank=True)
    dob = models.DateField(_("Date of Birth"), blank=True)

    # allow ad.._no and se.._no to be blank so they can be edited on post_save
    admission_no = models.CharField(_("admission no"), max_length=100, blank=True, editable=False)
    serial_no = models.CharField(_("Serial no"), max_length=50, editable=False, blank=True)

    klass = models.ForeignKey("Class", verbose_name=_("class"), on_delete=models.CASCADE)
    phone_no = models.CharField(_("phone number"), max_length=50, default='+123')
    email = models.EmailField(_("email"), max_length=254, null=True)
    gender = models.CharField(_("gender"), max_length=50,  choices=gender_choices)
    
    created_when = models.DateField(_('Registration date'), auto_now_add=True, null=True, editable=False)
    headshot = models.ImageField(upload_to='media/student_headshots', verbose_name=_('profile photo'), null=True)

    # private
    was_created = models.BooleanField(_("Was created"), editable=False, default=False, help_text=_('check if this object was fully created, stuff like admission_no do not need to be regenerated when this returns True'))

    def full_name(self):
        return _join(self.first_name, self.last_name)

    def age(self):
        return date.today().year - self.dob.year

    def _admission_no(self, model=None):
        # we can't use this function to generate admission number since it depends on time
        # we must on save generate it then save it then upon reference find *NOT generate it.
        self = model or self
        year = (self.created_when if self.created_when is not None else date.today()).year
        grade_code = self.klass.name
        serial_number = self._serial_no()

        return f"{year}/{grade_code}/{serial_number}"
    
    def _serial_no(self):
        '''Number in class'''
        class_mates = self.klass.student_set.order_by('id')  # including self
        for index, stud in enumerate(class_mates):
            if stud.id == self.id:
                break
        serial_num = index + 1 # serial number is the index of student in class
        return fill_zeros(serial_num)


    def get_gender(self):
        return self.gender_choices_dict[self.gender]
    
    def _resize_headshot(self):
        with self.headshot.open() as headshot:
            with Image.open(self.headshot) as img:
                size = (500, 500)
                with img.resize(size=size) as new_img:
                    new_img.save(headshot.path)
        
    
    def __str__(self):
        return self.full_name()
    
    def save(self, *a, **kw):
        super().save(*a, **kw)
        if not self.was_created:
            # fully create this model here only once in this models life time
            self.admission_no = self._admission_no()
            self.serial_no = self._serial_no()
            self.was_created = True
        self._resize_headshot()
        super().save()

 

class Class(models.Model):
    CRECHE = 'CRECHE'
    PRE_NURSERY = 'PRE_NUR'
    NURSERY_1 = 'NUR1'
    NURSERY_2 = 'NUR2'
    NURSERY_3 = 'NUR3'
    PRIMARY_1 = 'PRI1'
    PRIMARY_2 = 'PRI2'
    PRIMARY_3 = 'PRI3'
    PRIMARY_4 = 'PRI4'
    PRIMARY_5 = 'PRI5'
    PRIMARY_6 = 'PRI6'
    JSS_1 = 'JSS1'
    JSS_2 = 'JSS2'
    JSS_3 = 'JSS3'
    SSS_1 = 'SSS1'
    SSS_2 = 'SSS2'
    SSS_3 = 'SSS3'

    classes = [
        (CRECHE, 'CRECHE'),
        (PRE_NURSERY, 'PRE NURSERY'),
        (NURSERY_1, 'NURSERY 1'),
        (NURSERY_2, 'NURSERY 2'),
        (NURSERY_3, 'NURSERY 3'),
        (PRIMARY_1, 'PRIMARY 1'),
        (PRIMARY_2, 'PRIMARY 2'),
        (PRIMARY_3, 'PRIMARY 3'),
        (PRIMARY_4, 'PRIMARY 4'),
        (PRIMARY_5, 'PRIMARY 5'),
        (PRIMARY_6, 'PRIMARY 6'),
        (JSS_1, 'JUNIOR SECONDARY SCHOOL 1'),
        (JSS_2, 'JUNIOR SECONDARY SCHOOL 2'),
        (JSS_3, 'JUNIOR SECONDARY SCHOOL 3'),
        (SSS_1, 'SENIOR SECONDARY SCHOOL 1'),
        (SSS_2, 'SENIOR SECONDARY SCHOOL 2'),
        (SSS_3, 'SENIOR SECONDARY SCHOOL 3'),
    ]

    class_dict = dict(classes)

    name = models.CharField(_("Class Name"), max_length=150, choices=classes, unique=True)

    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
    

    def __str__(self):
        return self.class_dict[self.name]
    

class Subject(models.Model):
    name = models.CharField(_("subject name"), max_length=100)
    # teachers = models.ManyToManyField("admin.Admin", blank=True, null=True, verbose_name=_("Teachers"), help_text=_("Teachers who teach this course/subject."))
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name=_("class"), help_text=_("you should'nt be seeing this"))


# class Grade(models.Model):

#     grade_letter = models.CharField(help_text = _("eg. A, A1, B3"), max_length=50)
#     description = models.CharField(blank=True, max_length=50, help_text=_("eg. Excellent, Very Good, Good, Slow progress, Unsatisfactory"))
#     start = models.FloatField(max_length=4, default=0.0, help_text=_("grade min percentage"))
#     end = models.FloatField(max_length=4, default=100.0, help_text=_("grade max percentage"))



class Report(models.Model):
    terms = [
        ('FT', '1ST Term'),
        ('ST', '2ND Term'),
        ('TT', '3RD Term'),
    ]
    term_dict = dict(terms)

    term = models.CharField(max_length=200, help_text="term for this report eg. 1st Term", choices=terms)
    date = models.DateField(blank=True, default=timezone.now, help_text=_("date will show on report card"))
    # if you delete a class you delete all the reports
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, primary_key=False, verbose_name=_("class"), help_text="Which class ownes this report")
    # grade = models.OneToOneField(Grade, on_delete=models.CASCADE)
    
    def term_full(self):
        return self.term_dict[self.term]

    def __str__(self):
        return f"Report for {str(self.klass).lower()} {self.term_full()}"
    

class Test(models.Model):
    
    # a test/exam must be created under a *Report for grouping, and so that on_delete
    # all test/exam will be deleted
    test_names = [
        ('FCA', '1CA Test'),
        ('SCA', '2CA Test'),
    ]
    name = models.CharField(max_length=200, help_text="name of the test eg.First CA Test", choices=test_names)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    max_attainable = models.IntegerField(default=30, help_text=_("maximum score attainable for every subject in this test"))

    def __str__(self):
        return dict(self.test_names)[self.name]
    

class TestEntry(models.Model):
    subject = models.OneToOneField(Subject, help_text=_("subject eg. maths, eng"), on_delete=models.CASCADE)
    subject_score = models.IntegerField(help_text=_("score student had for this subject/course."))
    test = models.ForeignKey(Test, help_text=_("The test this entry belongs to."), on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Test Entry'
        verbose_name_plural = 'Test Entries'


class Exam(models.Model):
    name = models.CharField(max_length=200, help_text="name of the exam eg.First Semester Exam")
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, help_text=_("student who ownes this exam report"), on_delete=models.CASCADE, null=True)


class ExamEntry(models.Model):
    subject = models.OneToOneField(Subject, help_text=_("subject eg. maths, eng"), on_delete=models.CASCADE)
    subject_score = models.IntegerField(help_text=_("score student had for this subject/course."))
    exam = models.ForeignKey(Exam, help_text=_("The test this entry belongs to."), on_delete=models.CASCADE)
    

    class Meta:
        verbose_name = _("Exam Entry")
        verbose_name_plural = _("Exam Entries")



