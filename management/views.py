from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from quiz.models import Mark, Question
from os.path import join
import csv
import logging
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from os.path import join

# Create your views here.
@method_decorator(staff_member_required, name="dispatch")
class Manage(View):
    def get(self, request):
        panel_options = {
            "Upload Questions": {
                "link": reverse("upload_question"),
                "btntxt": "Upload"
            },
            "Verify Questions": {
                "link": reverse("verify_question"),
                "btntxt": "Verify"
            },
            "Get Results": {
                "link": reverse("results"),
                "btntxt": "Get"
            }
        }
        return render(
            request,
            "management/manage.html",
            {"panel_options": panel_options}
        )

@method_decorator(staff_member_required, name="dispatch")
class Results(View):
    def get(self, request):
        return render(request, "management/results.html", {"results": Mark.objects.all()})

# Set up logging
logger = logging.getLogger(__name__)
class UploadQuestion(View):
    def get(self, request):
        return render(request, "management/upload_question.html")

    def post(self, request):
        qFile = request.FILES["qFile"]
        if not str(qFile).endswith(".csv"):
            messages.warning(request, "Only CSV file allowed")
            return redirect("manage")
        
        filepath = join(settings.BASE_DIR, "upload", "questions.csv")
        with open(filepath, "wb") as f:
            for chunk in qFile.chunks():
                f.write(chunk)
        
        # Process the CSV file and save questions to the database
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        logger.debug(f"Processing row: {row}")
                        creator_id = row.get('creator_id')
                        if not creator_id:
                            logger.error("Missing creator_id in row")
                            continue

                        creator = User.objects.get(id=creator_id)
                        
                        verified_str = row.get('verified', '').strip().lower()
                        verified = verified_str in ['true', '1', 't', 'yes']

                        Question.objects.create(
                            question=row['question'],
                            option1=row['option1'],
                            option2=row['option2'],
                            option3=row['option3'],
                            option4=row['option4'],
                            correct_option=row['correct_option'],
                            creator=creator,
                            verified=verified,
                            subject=row['subject']  # New field
                        )
                    except ObjectDoesNotExist:
                        logger.error(f"User with id {row['creator_id']} does not exist.")
                        messages.error(request, f"User with id {row['creator_id']} does not exist.")
                    except KeyError as e:
                        logger.error(f"Missing column in CSV: {e}")
                        messages.error(request, f"Missing column in CSV: {e}")
                    except Exception as e:
                        logger.error(f"Error processing CSV row: {e}")
                        messages.error(request, f"Error processing CSV: {e}")
            
            messages.success(request, "CSV file uploaded and questions imported successfully")
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            messages.error(request, f"Error reading CSV file: {e}")
        
        return redirect("manage")
# class UploadQuestion(View):
#     def get(self, request):
#         return render(request, "management/upload_question.html")

#     def post(self, request):
#         qFile = request.FILES["qFile"]
#         if not str(qFile).endswith(".csv"):
#             messages.warning(request, "Only CSV file allowed")
#             return redirect("manage")
        
#         filepath = join(settings.BASE_DIR, "upload", "questions.csv")
#         with open(filepath, "wb") as f:
#             for chunk in qFile.chunks():
#                 f.write(chunk)
        
#         # Process the CSV file and save questions to the database
#         try:
#             with open(filepath, newline='', encoding='utf-8') as csvfile:
#                 reader = csv.DictReader(csvfile)
#                 for row in reader:
#                     try:
#                         logger.debug(f"Processing row: {row}")
#                         creator_id = row.get('creator_id')
#                         if not creator_id:
#                             logger.error("Missing creator_id in row")
#                             continue

#                         creator = User.objects.get(id=creator_id)
                        
#                         verified_str = row.get('verified', '').strip().lower()
#                         verified = verified_str in ['true', '1', 't', 'yes']

#                         Question.objects.create(
#                             question=row['question'],
#                             option1=row['option1'],
#                             option2=row['option2'],
#                             option3=row['option3'],
#                             option4=row['option4'],
#                             correct_option=row['correct_option'],
#                             creator=creator,
#                             verified=verified
#                         )
#                     except ObjectDoesNotExist:
#                         logger.error(f"User with id {row['creator_id']} does not exist.")
#                         messages.error(request, f"User with id {row['creator_id']} does not exist.")
#                     except KeyError as e:
#                         logger.error(f"Missing column in CSV: {e}")
#                         messages.error(request, f"Missing column in CSV: {e}")
#                     except Exception as e:
#                         logger.error(f"Error processing CSV row: {e}")
#                         messages.error(request, f"Error processing CSV: {e}")
            
#             messages.success(request, "CSV file uploaded and questions imported successfully")
#         except Exception as e:
#             logger.error(f"Error reading CSV file: {e}")
#             messages.error(request, f"Error reading CSV file: {e}")
        
#         return redirect("manage")
# @method_decorator(staff_member_required, name="dispatch")
# class UploadQuestion(View):
#     def get(self, request):
#         return render(request, "management/upload_question.html")

#     def post(self, request):
#         qFile = request.FILES["qFile"]
#         if not str(qFile).endswith(".csv"):
#             messages.warning(request, "Only CSV file allowed")
#             return redirect("manage")
        
#         filepath = join(settings.BASE_DIR, "upload", "questions.csv")
#         with open(filepath, "wb") as f:
#             for chunk in qFile.chunks():
#                 f.write(chunk)
        
#         # Process the CSV file and save questions to the database
#         try:
#             with open(filepath, newline='', encoding='utf-8') as csvfile:
#                 reader = csv.DictReader(csvfile)
#                 for row in reader:
#                     try:
#                         creator = User.objects.get(id=row['creator_id'])
#                         verified = row['verified'].strip().lower() in ['true', '1', 't', 'yes']
#                         Question.objects.create(
#                             question=row['question'],
#                             option1=row['option1'],
#                             option2=row['option2'],
#                             option3=row['option3'],
#                             option4=row['option4'],
#                             correct_option=row['correct_option'],
#                             creator=creator,
#                             verified=verified
#                         )
#                     except ObjectDoesNotExist:
#                         messages.error(request, f"User with id {row['creator_id']} does not exist.")
#                         return redirect("manage")
#                     except KeyError as e:
#                         messages.error(request, f"Missing column in CSV: {e}")
#                         return redirect("manage")
#                     except Exception as e:
#                         messages.error(request, f"Error processing CSV: {e}")
#                         return redirect("manage")
            
#             messages.success(request, "CSV file uploaded and questions imported successfully")
#         except Exception as e:
#             messages.error(request, f"Error reading CSV file: {e}")
        
#         return redirect("manage")
# class UploadQuestion(View):
#     def get(self, request):
#         return render(request, "management/upload_question.html")

#     def post(self, request):
#         qFile = request.FILES["qFile"]
#         filepath = join(settings.BASE_DIR, "upload", "questions.csv")
#         if not str(qFile).endswith(".csv"):
#             messages.warning(request, "Only CSV file allowed")
#         else:
#             with open(filepath, "wb") as f:
#                 for chunk in qFile.chunks():
#                     f.write(chunk)
#             messages.success(request, "CSV file uploaded")
#         return redirect("manage")

@method_decorator(staff_member_required, name="dispatch")
class VerifyQuestion(View):
    def get(self, request):
        qs = Question.objects.filter(verified=False)
        return render(request, "management/verify_question.html", {"questions": qs})

    def post(self, request):
        count = 0
        for q, v in request.POST.items():
            if q.startswith("q") and v == "on":
                id = q[1:]
                q = Question.objects.filter(id=id).first()
                if q is not None:
                    q.verified = True
                    q.save()
                    count += 1
                else:
                    messages.warning(request, f"No question exists with id {id}")
        messages.success(request, f"{count} questions added")
        return redirect("manage")

@method_decorator(staff_member_required, name="dispatch")
class Setting(View):
    def get(self, request):
        info = {
            "question_limit": settings.GLOBAL_SETTINGS["questions"]
        }
        return render(request, "management/setting.html", {"info": info})

    def post(self, request):
        qlimit = int(request.POST.get("qlimit", 10))
        if qlimit > 0:
            settings.GLOBAL_SETTINGS["questions"] = qlimit
            messages.success(request, "You preference saved")
        else:
            messages.warning(request, "Question limit can't be 0 or less than 0")
        return redirect("setting")
