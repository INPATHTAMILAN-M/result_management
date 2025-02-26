import pandas as pd
from django.shortcuts import render,redirect
from .models import ExamResult
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from captcha.fields import CaptchaField
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from .forms import MatchForm
from django.contrib import messages


def admin_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('upload_page')  
            else:
                # Add a non-field error if the credentials are invalid
                form.add_error(None, "Invalid email or password.")
        else:
            # Handle case where form is not valid, including invalid email
            pass
    else:
        form = LoginForm()

    return render(request, 'admin_login.html', {'form': form})


@login_required
def upload_exam_results(request):
    if request.method == 'POST' and 'clear_data' in request.POST:
        ExamResult.objects.all().delete()
        messages.success(request, "All data has been cleared successfully!")
        return redirect('upload_page')

    if request.method == 'POST' and request.FILES['exam_data']:
        exam_file = request.FILES['exam_data']
        try:
            df = pd.read_excel(exam_file)

            error_rows = []
            success_count = 0

            required_fields = [
                # 'Exam Code', 'Exam Name', 'Regulation', 'Batch', 'Programme Code', 
                'Programme Name',
                'Semester', 
                # 'Section', 
                'Register No.', 'Student Name', 'Date of Birth', 'Course Code',
                'Course Name', 
                # 'Course Index', 'Course Credit', 
                'Regular/Arrear', 
                # 'Internal', 'External','Total', 
                'Exam Result', 'Grade Code', 
                # 'Grade Point'
            ]

            for index, row in df.iterrows():
                try:
                    # Check if any required field is missing
                    
                    for field in required_fields:
                        if pd.isna(row[field]):
                            error_rows.append(f"Row {index + 1}: Missing {field} for {row['Student Name']}")
                            break  
                    else:
                            # Handle and validate Date of Birth format
                        try:
                            # Try to convert the 'Date of Birth' to the correct format (YYYY-MM-DD)
                            date_of_birth = pd.to_datetime(row['Date of Birth'], errors='coerce', dayfirst=True)
                            if pd.isna(date_of_birth):
                                error_rows.append(f"Row {index + 1}: Invalid Date of Birth format for {row['Student Name']}. Expected format is YYYY-MM-DD.")
                                continue  # Skip this row
                            row['Date of Birth'] = date_of_birth.strftime('%Y-%m-%d')  # Reformat to YYYY-MM-DD
                        except Exception as e:
                            error_rows.append(f"Row {index + 1}: Error processing Date of Birth for {row['Student Name']} - {str(e)}")
                            continue
                        is_revaluation=request.POST.get('is_revaluation') == 'true'
                        # Check for duplicate entry based on register_no, exam_code, and dob
                        if is_revaluation:
                            duplicate_exists = ExamResult.objects.filter(
                                register_no=row['Register No.'],
                                course_code=row['Course Code'],
                                date_of_birth=row['Date of Birth'],
                                is_revaluation=True
                            ).exists()
                            is_revaluation = True
                        else:
                            duplicate_exists = ExamResult.objects.filter(
                                register_no=row['Register No.'],
                                course_code=row['Course Code'],
                                date_of_birth=row['Date of Birth'],
                                is_revaluation=False
                            ).exists()
                            is_revaluation = False

                        if duplicate_exists:
                            error_rows.append(f"Row {index + 1}: Duplicate entry for Register No. {row['Register No.']}, Exam Code {row['Exam Code']}, and Date of Birth {row['Date of Birth']}")
                        else:
                            # If no duplicate, save the record
                            exam_result = ExamResult(
                                
                                exam_code=row.get('Exam Code', 'N/A'),
                                exam_name=row.get('Exam Name', 'N/A'),
                                regulation=row.get('Regulation', 'N/A'),
                                batch=row.get('Batch', 'N/A'),
                                programme_code=row.get('Programme Code', 'N/A'),
                                programme_name=row.get('Programme Name', 'N/A'),
                                semester=row.get('Semester', 'N/A'),
                                section=row.get('Section', 'N/A'),
                                register_no=row.get('Register No.', 'N/A'),
                                student_name=row.get('Student Name', 'N/A'),
                                date_of_birth=row.get('Date of Birth', 'N/A'),
                                course_code=row.get('Course Code', 'N/A'),
                                course_name=row.get('Course Name', 'N/A'),
                                course_index=row.get('Course Index', '0'),
                                course_credit=row.get('Course Credit', 0),  # Default value of 0 for credit
                                regular_or_arrear=row.get('Regular/Arrear', 'N/A'),
                                internal_marks=row.get('Internal', 0),  # Default value of 0 for internal marks
                                external_marks=row.get('External', 0),  # Default value of 0 for external marks
                                total_marks=row.get('Total', 0),  # Default value of 0 for total marks
                                exam_result=row.get('Exam Result', 'N/A'),
                                grade_code=row.get('Grade Code', 'N/A'),
                                grade_point=row.get('Grade Point', 0),
                                is_revaluation=is_revaluation,
                            )
                            exam_result.save()
                            success_count += 1

                except Exception as e:
                    error_rows.append(f"Row {index + 1}: Error processing row - {str(e)}")
                    continue

            return render(request, 'upload_page.html', {
                'success_count': success_count,
                'error_rows': error_rows,
            })

        except Exception as e:
            return HttpResponse(f"Error reading file: {str(e)}")
    
    return render(request, 'upload_page.html')


def student_login(request):
    error = None
    data_matched = None

    if request.method == 'POST':
        form = MatchForm(request.POST)

        if form.is_valid():  # This validates the entire form including CAPTCHA
            register_no = form.cleaned_data['register_no']
            dob = form.cleaned_data['dob']
            is_revaluation = request.POST.get('is_revaluation') == 'true' 
            # Look for matching exam results
            if is_revaluation:
                data_matched = ExamResult.objects.filter(register_no=register_no, date_of_birth=dob, is_revaluation=True)
            else:
                data_matched = ExamResult.objects.filter(register_no=register_no, date_of_birth=dob, is_revaluation=False)

            if data_matched.exists():
                data_matched_list = [
                    {
                        **result,
                        'date_of_birth': result['date_of_birth'].strftime('%Y-%m-%d') 
                    }
                    for result in data_matched.values()
                ]
                request.session['data_matched'] = data_matched_list
                return redirect('results')  
            else:
                error = "No matching data found for the given Registration Number and Date of Birth."
        else:
            # Handle CAPTCHA error separately
            if 'captcha' in form.errors:
                error = "Incorrect CAPTCHA. Please try again."
                # Reset the captcha field by setting it to None
                form.fields['captcha'].widget.attrs['value'] = ''  # This will "reset" the CAPTCHA field

            else:
                error = "Invalid form data. Please check your input and try again."

    else:
        form = MatchForm()

    return render(request, 'student_login.html', {'form': form, 'error': error})

def results(request):
    data_matched = request.session.get('data_matched', None)
    
    if data_matched:
        return render(request, 'results.html', {'data_matched': data_matched})
    else:
        return HttpResponse("No data to display. Please try again.", status=404)
