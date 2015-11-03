from django.conf import settings
from profile.models import Profile_emp
from django.utils.translation import ugettext_lazy as _
from article.models import Article

def get_user_status(request):
    """ context processor to get user status real profile or anonymous """

    u = request.user
    print '_____________________________'
    print u


    if request.user.is_authenticated():

        # if admin is logged in return nothing
        if u.is_superuser:
            return {'request': request}
        
        profile = u.get_profile()

        if profile.is_candid:
            real_profile = u.profile_candid
        else:
            real_profile = u.profile_emp
    else:
        real_profile = u
            
    return {'request': request, 'real_profile': real_profile }
