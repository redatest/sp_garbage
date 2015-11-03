from django import template

register = template.Library()

def callMethod(obj, methodName):
	method = getattr(obj, methodName)

	if obj.__dict__.has_key("__callArg"):
		ret = method(*obj.__callArg)
		del obj.__callArg
		return ret

	return method()

def args(obj, arg, arg2):
	if not obj.__dict__.has_key("__callArg"):
		obj.__callArg = []

	obj.__callArg += arg
	obj.__callArg += arg2
	return obj

register.filter("call", callMethod)
register.filter("args", args)
