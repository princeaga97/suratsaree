from django.contrib.sessions.models import Session
from accounts.models import LoggedInUser
from django.contrib.auth.models import User
import datetime
from core.models import UserProfile

class OneSessionPerUserMiddleware:
    # Called only once when the web server starts
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated and not request.user.is_staff:
            session_key = request.session.session_key
            try:
                logged_in_user = request.user.logged_in_user
                stored_session_key = logged_in_user.session_key
                userprofile = request.user.userprofile
                count = logged_in_user.count
                date_today = datetime.date.today()
                # stored_session_key exists so delete it if it's different
                if count <=20:
                    if request.user.userprofile.valid_till:
                        if  request.user.userprofile.valid_till >=  datetime.date(year= int(date_today.year), month = int(date_today.month) , day = int(date_today.day)):
                            if stored_session_key != session_key:
                                count = count+1
                            logged_in_user.session_key = session_key
                            logged_in_user.count =count
                            logged_in_user.save()
                        else:
                            request.user.userprofile.one_click_purchasing = False
                            request.user.userprofile.save()
                            if stored_session_key != session_key:
                                count = count+1
                            logged_in_user.session_key = session_key
                            logged_in_user.count =count
                            logged_in_user.save()

                    else:
                        if stored_session_key != session_key:
                            count = count+1
                        logged_in_user.session_key = session_key
                        logged_in_user.count =count
                        logged_in_user.save()
                else:
                    user = User.objects.get(id = request.user.id)
                    logged_in_user.count = 0
                    logged_in_user.save()
                    user.is_active = False
                    user.save()

            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=request.user,rate_type=0)
                logged_in_user.session_key = session_key
                logged_in_user.save()
            except LoggedInUser.DoesNotExist:
                LoggedInUser.objects.create(user=request.user, session_key=session_key)




        response = self.get_response(request)

        # This is where you add any extra code to be executed for each request/response after
        # the view is called.
        # For this tutorial, we're not adding any code so we just return the response

        return response