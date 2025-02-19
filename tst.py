import pandas as pd
import random
from faker import Faker

fake = Faker()

# Define constants
NUM_ENTRIES = 5000
EXAM_CODE = "NOV22"
EXAM_NAME = "NOV / DEC 2022"
REGULATION = "2021"
BATCH = "2021-2025"
PROGRAMME_CODE = "CIVIL"
PROGRAMME_NAME = "B.E., CIVIL ENGINEERING"
SEMESTER = 3
SECTIONS = ["A", "B", "C"]
COURSE_CODES = ["21MA201", "21MA202", "21MA203", "21MA204", "21MA205"]
COURSE_NAMES = [
    "Transforms and Partial Differential Equations",
    "Numerical Methods",
    "Probability and Statistics",
    "Discrete Mathematics",
    "Linear Algebra"
]
COURSE_INDICES = list(range(15, 20))
COURSE_CREDITS = [4, 3, 4, 3, 4]
GRADE_CODES = ["A", "B", "C"]
GRADE_POINTS = [8, 7, 6]

# Generate data
data = []
used_combinations = set()

# Create a dictionary to store the number of courses assigned to each student
student_courses = {}

for _ in range(NUM_ENTRIES):
    while True:
        register_no = fake.unique.random_number(digits=9, fix_len=True)
        dob = fake.date_of_birth(minimum_age=18, maximum_age=22).strftime("%d-%m-%Y")
        
        # Check if this register_no + dob combination has already been assigned 6 courses
        if (register_no, dob) not in student_courses:
            student_courses[(register_no, dob)] = 0
        
        if student_courses[(register_no, dob)] < 6:
            # Select a unique set of 6 course_codes for this student
            remaining_courses = random.sample(COURSE_CODES, 5)  # Choose 5 courses randomly
            remaining_courses.append(random.choice(COURSE_CODES))  # Adding a 6th course randomly
            random.shuffle(remaining_courses)  # Shuffle the courses to avoid order bias
            break

    # Generate data for each course associated with the same register_no and dob
    for course_code in remaining_courses:
        student_name = fake.name()
        section = random.choice(SECTIONS)
        internal = random.randint(20, 40)
        external = random.randint(30, 50)
        total = internal + external
        exam_result = "P" if total >= 50 else "F"
        grade_code = random.choice(GRADE_CODES)
        grade_point = GRADE_POINTS[GRADE_CODES.index(grade_code)]

        data.append([
            EXAM_CODE, EXAM_NAME, REGULATION, BATCH, PROGRAMME_CODE, PROGRAMME_NAME,
            SEMESTER, section, register_no, student_name, dob, course_code,
            COURSE_NAMES[COURSE_CODES.index(course_code)], COURSE_INDICES[COURSE_CODES.index(course_code)],
            COURSE_CREDITS[COURSE_CODES.index(course_code)], "R", internal, external, total,
            exam_result, grade_code, grade_point
        ])

        # Increment the course count for this student
        student_courses[(register_no, dob)] += 1

# Create DataFrame
columns = [
    "Exam Code", "Exam Name", "Regulation", "Batch", "Programme Code", "Programme Name",
    "Semester", "Section", "Register No.", "Student Name", "Date of Birth", "Course Code",
    "Course Name", "Course Index", "Course Credit", "Regular/Arrear", "Internal", "External",
    "Total", "Exam Result", "Grade Code", "Grade Point"
]
df = pd.DataFrame(data, columns=columns)

# Save to Excel
df.to_excel("student_exam_results.xlsx", index=False)
