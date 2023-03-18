from PIL import Image

from pprint import pprint

from datetime import date

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


from core import settings

_is_neg = lambda x: x<0

_join = lambda *a: ' '.join([(str(i) if i else '') for i in a])

def fill_zeros(num, digits=3):
    '''Fill number with preceeding zeroes eg. 003 '''
    serial_number = str(num)
    zeros = (digits - len(serial_number))
    zeros = '0' * zeros if not _is_neg(zeros) else ''
    return zeros + serial_number


def _model_exist(model, **kw):
    return model.objects.filter(**kw).first()

from django.contrib.auth.models import AbstractUser
# once a student is created it cant log in it is not a staff
# class Student(AbstractUser)
class Student(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    gender_choices = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    gender_choices_dict = dict(gender_choices)

    first_name = models.CharField(_("student name"), max_length=200, help_text=_("Name of student"))
    last_name = models.CharField(_("last name"), max_length=200, help_text=_("Surname of student"), null=True, blank=True, default="")
    middle_name = models.CharField(_("middle name"), max_length=200, help_text=_("Other name"), null=True, blank=True, default="")
    dob = models.DateField(_("Date of Birth"))

    # allow ad.._no and se.._no to be blank so they can be edited on post_save
    admission_no = models.CharField(_("admission no"), max_length=100, editable=False, blank=True)
    serial_no = models.CharField(_("Serial no"), max_length=50, editable=False, blank=True)

    klass = models.ForeignKey("Class", verbose_name=_("class"), on_delete=models.CASCADE)
    phone_no = models.CharField(_("phone number"), max_length=50, default='+123')

    # while dispersing results check if this email field is not set then raise warnings to user of students that didnt' have emails
    # so they coulnd recieve results

    email = models.EmailField(_("email"), max_length=254, null=True)



    gender = models.CharField(_("gender"), max_length=50,  choices=gender_choices)
    
    created_when = models.DateField(_('when field was created'), auto_now_add=True, editable=False)
    registration_date = models.DateField(_("Registration date"), default=timezone.now, )

    address = models.CharField(_("Address"), max_length=1500, default='', blank=True, null=True)

    # Student must have profile photo I'm just allowing this for now
    headshot = models.ImageField(upload_to='media/student_headshots', verbose_name=_('profile photo'), null=True)

    # private
    was_created = models.BooleanField(_("Was created"), editable=False, default=False, help_text=_('check if this object was fully created, stuff like admission_no do not need to be regenerated when this returns True'))


    def delta(self):
        # how long has it been since this student was created.
        return (timezone.now().date() - self.created_when).days

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




def get_recent_students(days_behind=5, max=None):
    # get students who were registered less than specified date (*days_behind)
    if max is not None and max<1:
        raise TypeError("Set max to a number greater than 0")
    counter = 0
    for student in Student.objects.all():
        if student.delta() <= days_behind:
            if isinstance(max, int) and counter>=max:
                break
            yield student
            counter += 1

                
 

class Guardian(models.Model):
    GUARDIAN = 'GD'
    MOTHER = 'MT'
    FATHER = 'FT'
    UNCLE = 'UN'
    AUNTY = 'AT'
    BROTHER = 'BR'
    SISTER = 'ST'
    GRANDFATHER = 'GRDFT'
    GRANDMOTHER = 'GRDMT'

    relationships = [
        (GUARDIAN, 'Guardian'),
        (MOTHER, 'Mother'),
        (FATHER, 'Father'),
        (UNCLE, 'Uncle'),
        (AUNTY, 'Aunty'),
        (BROTHER, 'Brother'),
        (SISTER, 'Sister'),
        (GRANDFATHER, 'Grand Father'),
        (GRANDMOTHER, 'Grand Mother'),
    ]

    rel_dict = dict(relationships)

    MALE = 'M'
    FEMALE = 'F'


    gender_choices = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    
    gender_choices_dict = dict(gender_choices)


    full_name = models.CharField(_("full_name"), max_length=250)
    student = models.ForeignKey(Student, verbose_name=_("child of this gaurdian"), on_delete=models.CASCADE)
    relationship = models.CharField(_("Relationship with child"), max_length=50, choices=relationships, default=GUARDIAN)
    phone_no = models.CharField(_("phone number"), max_length=200, blank=True, null=True)
    email = models.EmailField(_("email"), max_length=254)
    gender = models.CharField(_("gender"), max_length=50, choices=gender_choices)

    address = models.CharField(_("Address"), max_length=3500, default="", blank=True, null=True)
    occupation = models.CharField(_("Address"), max_length=250, default="", blank=True, null=True)


    def get_relationship(self):
        return self.rel_dict[self.relationship]

    def get_gender(self):
        return self.gender_choices_dict[self.gender]

    def __str__(self):
        return self.full_name


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

    ALL_CLASSES_TICK = 'ALL CLASSES'    # SOME SUBJECTS MAY NEED TO BELONG TO ALL CLASSES


    class_dict = dict(classes)
    _class_dict_rev = dict(zip(class_dict.values(), class_dict.keys()))

    name = models.CharField(_("Class Name"), max_length=150, choices=classes, unique=True)

    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
    

    def __str__(self):
        return self.class_dict[self.name]
    

class Subject(models.Model):
    # experimental can we have
    name = models.CharField(_("subject name"), max_length=100, null=True)
    # teachers = models.ManyToManyField("admin.Admin", blank=True, null=True, verbose_name=_("Teachers"), help_text=_("Teachers who teach this course/subject."))
    klass = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name=_("class"), help_text=_("you should'nt be seeing this"), null=True)
    for_all_class = models.BooleanField(_("for all class"), default=False, help_text=_("is this subject for all class"))

    
    def __str__(self):
        return self.name
    

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        # pprint(update_fields)   # lets see what's under the hood
        self.name = self.name.strip().lower()
        super().save()



class Report(models.Model):
    terms = [
        ('FT', '1ST Term'),
        ('ST', '2ND Term'),
        ('TT', '3RD Term'),
    ]
    term_dict = dict(terms)

    term = models.CharField(max_length=200, help_text="term for this report eg. 1st Term", choices=terms)
    year = models.CharField(max_length=5)
    session = models.CharField(max_length=200)
    grading = models.JSONField(null=True)
    # klass = models.ForeignKey(Class, on_delete=models.CASCADE, primary_key=False, verbose_name=_("class"), help_text="Which class ownes this report")
    # grade = models.OneToOneField(Grade, on_delete=models.CASCADE)
    
    def term_full(self):
        return self.term_dict[self.term]

    def __str__(self):
        return f"Report for {self.term_full()}"
        
    
class ReportClass(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    klass = models.ForeignKey(Class, on_delete=models.CASCADE)
    

class ReportStudent(models.Model):
    rep_klass = models.ForeignKey(ReportClass, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    

class ReportSubject(models.Model):
    rep_stud = models.ForeignKey(ReportStudent, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    # scores
    t1 = models.PositiveIntegerField(null=True)
    t2 = models.PositiveIntegerField(null=True)
    t3 = models.PositiveIntegerField(null=True)
    project = models.PositiveIntegerField(null=True)
    exam = models.PositiveIntegerField(null=True)


# utilities #########################################################################

