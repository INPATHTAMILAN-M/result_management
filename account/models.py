from django.db import models

class ExamResult(models.Model):
 
    # exam info
    exam_code = models.CharField(max_length=10)
    exam_name = models.CharField(max_length=50)
    regulation = models.CharField(max_length=10)
    batch = models.CharField(max_length=15)
    programme_code = models.CharField(max_length=10)
    programme_name = models.CharField(max_length=100)
    semester = models.CharField(max_length=10)
    section = models.CharField(max_length=10)

    # student info
    register_no = models.CharField(max_length=20)
    student_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    # course info
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)
    course_index = models.IntegerField()
    course_credit = models.IntegerField()

    # exam details
    regular_or_arrear = models.CharField(max_length=10)
    internal_marks = models.IntegerField()
    external_marks = models.IntegerField()
    total_marks = models.IntegerField()

    # result info
    exam_result = models.CharField(max_length=10)
    grade_code = models.CharField(max_length=2)
    grade_point = models.IntegerField()

    status = models.CharField(max_length=5)
    is_revaluation = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.student_name} - {self.course_name} ({self.exam_name})"

