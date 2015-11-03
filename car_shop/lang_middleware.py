def force_lang(self, request):
    if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
        del request.META['HTTP_ACCEPT_LANGUAGE']