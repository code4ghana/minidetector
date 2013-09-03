from django import middleware
from django.http import HttpResponseRedirect
from minidetector import settings as minidetector_settings
from minidetector.useragents import search_strings
import inspect

class Middleware(object):
    @staticmethod
    def process_request(request):
        """ Adds a "mobile" attribute to the request which is True or False
            depending on whether the request should be considered to come from a
            small-screen device such as a phone or a PDA"""
        if hasattr(request, 'session') and minidetector_settings.USE_SESSIONS:
            # session enabled
            if not request.session.get('mobile_checked', False):
                # haven't checked if mobile yet - put in request and session
                Middleware.configure_request(request)
                Middleware.set_session_from_request(request)
                request.session['mobile_checked'] = True
                if request.mobile:
                    mobile_redirect = Middleware.get_mobile_redirect(request)
                    if mobile_redirect:
                        return mobile_redirect
            else:
                # Make sure it doesn't try this again
                Middleware.set_request_from_session(request)
        else:
            # sessions disabled - always do the work
            Middleware.configure_request(request)
            if request.mobile:
                mobile_redirect = Middleware.get_mobile_redirect(request)
                if mobile_redirect:
                    return mobile_redirect
        return None
    
    @staticmethod
    def get_mobile_redirect(request):
        if not minidetector_settings.MOBILE_URL:
            return None
        subs = {
            'host': request.get_host(),
            'path': request.path,
            'full_path': request.get_full_path(),
        }
        mobile_url = minidetector_settings.MOBILE_URL.format(**subs)
        return HttpResponseRedirect(mobile_url)
        

    @staticmethod
    def set_session_from_request(request):
        request.session['mobile'] = request.mobile
        request.session['wap'] = request.wap
        request.session['browser_is_android'] = request.browser_is_android
        request.session['browser_is_ios'] = request.browser_is_ios
        request.session['browser_is_ipad'] = request.browser_is_ipad
        request.session['browser_is_iphone'] = request.browser_is_iphone
        request.session['browser_is_webkit'] = request.browser_is_webkit
        request.session['mobile_device'] = request.mobile_device
        request.session['touch_device'] = request.touch_device
        request.session['wide_device'] = request.wide_device

    @staticmethod
    def set_request_from_session(request):
        request.mobile = request.session['mobile']
        request.wap = request.session['wap']
        request.browser_is_android = request.session['browser_is_android']
        request.browser_is_ios = request.session['browser_is_ios']
        request.browser_is_ipad = request.session['browser_is_ipad']
        request.browser_is_iphone = request.session['browser_is_iphone']
        request.browser_is_webkit = request.session['browser_is_webkit']
        request.mobile_device = request.session['mobile_device']
        request.touch_device = request.session['touch_device']
        request.wide_device = request.session['wide_device']

    @staticmethod
    def configure_request(request):
        # default all possible attributes for desktop
        request.mobile = False
        request.wap = False
        request.browser_is_android = False
        request.browser_is_ios = False
        request.browser_is_ipad = False
        request.browser_is_iphone = False
        request.browser_is_webkit = False
        request.mobile_device = ''
        request.touch_device = False
        request.wide_device = True

        if request.META.has_key("HTTP_X_OPERAMINI_FEATURES"):
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            request.mobile = True
            return

        if request.META.has_key("HTTP_ACCEPT"):
            s = request.META["HTTP_ACCEPT"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                # Then it's a wap browser
                request.mobile = True
                request.wap = True
                return

        if request.META.has_key("HTTP_USER_AGENT"):
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            s = request.META["HTTP_USER_AGENT"].lower()
            print "checking user agent", s

            if 'applewebkit' in s:
                request.browser_is_webkit = True

            # some special checks for 'important' devices
            if 'ipad' in s:
                request.browser_is_ipad = True
                request.browser_is_ios = True

                request.mobile_device = 'ipad'
                request.touch_device = True
                request.wide_device = True

                # toggle setting for deciding if ipad is mobile or not
                request.mobile = minidetector_settings.IPAD_IS_MOBILE
                return

            if 'iphone' in s or 'ipod' in s:
                request.browser_is_iphone = True
                request.browser_is_ios = True

                request.mobile_device = 'iphone'
                request.touch_device = True
                request.wide_device = False

                # toggle setting for deciding if iphone is mobile or not
                request.mobile = minidetector_settings.IPHONE_IS_MOBILE
                return

            if 'android' in s:
                request.browser_is_android = True

                request.mobile_device = 'android'
                request.touch_device = True
                request.wide_device = False

                # toggle setting for deciding if iphone is mobile or not
                request.mobile = minidetector_settings.ANDROID_IS_MOBILE
                return

            for ua in search_strings:
                if ua in s:
                    request.mobile = True
                    return

def detect_mobile(view):
    """ View Decorator that adds a "mobile" attribute to the request which is
        True or False depending on whether the request should be considered
        to come from a small-screen device such as a phone or a PDA"""

    arguments=inspect.getargspec(view)[0]
    if len(arguments) and (arguments[0]=='self'):
        #class based view
        def detected(self,request,*args,**kwargs):
            Middleware.process_request(request)
            return view(self,request, *args, **kwargs)
        detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
        return detected

    def detected(request, *args, **kwargs):
        Middleware.process_request(request)
        return view(request, *args, **kwargs)
    detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
    return detected


__all__ = ['Middleware', 'detect_mobile']
