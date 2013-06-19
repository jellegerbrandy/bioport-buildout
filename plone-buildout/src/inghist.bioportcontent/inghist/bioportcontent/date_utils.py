#from Products.PageTemplates.GlobalTranslationService import getGlobalTranslationService
from zope.i18n import translate 
from Products.CMFPlone import i18nl10n

def translate_month(month_index, language): 
    month_id = i18nl10n.monthname_msgid(month_index)
#    ts = getGlobalTranslationService()
#    return ts.translate(domain='plonelocales', msgid=month_id, target_language=language)
    return translate(domain='plonelocales', msgid=month_id, target_language=language)

