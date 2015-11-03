
from functools import wraps
from profile.models import Profile_candid, Profile_emp
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import HttpResponseRedirect, RequestContext


def set_notification_message(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        msg, profile     = None, None
        if request.user.is_authenticated():
            u            = request.user
            user_profile = u.get_profile()

            if user_profile.is_candid:
                try:
                    profile = u.profile_candid
                except Exception, e:
                    u.delete() # delete user if subscription went wrong
                    auth_logout(request)
                    return HttpResponseRedirect('/')
                else:
                    msg = profile.get_all_fields()
            else:
                try:
                    profile = u.profile_emp
                except Exception, e:
                    u.delete() # delete user if subscription went wrong
                    auth_logout(request)
                    return HttpResponseRedirect('/')
                else:
                    msg = profile.get_all_fields()
        else:
            msg, profile     = None, None

        return view(request, msg, profile, *args, **kwargs)
    return wrapper


def restrict_candidate(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):

        real_profile = RequestContext(request).get('real_profile')
        if not isinstance(real_profile, Profile_candid):
            return HttpResponseRedirect('/')                        

        return view(request, *args, **kwargs)
    return wrapper


def restrict_employer(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):

        real_profile = RequestContext(request).get('real_profile')
        if not isinstance(real_profile, Profile_emp):
            return HttpResponseRedirect('/')                        

        return view(request, *args, **kwargs)
    return wrapper
