from django import template


register = template.Library()


@register.filter(name='index')
def index(value, ind):
    return value[ind]

@register.filter(name='indexR')
def indexR(value, ind):
    try:
        return value[ind]['room']
    except:
        return ''

@register.filter(name='indexS')
def indexS(value, ind):
    try:
        return value[ind]['secName']
    except:
        return ''