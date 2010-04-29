from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import i18nl10n
from Products.PageTemplates.GlobalTranslationService import getGlobalTranslationService
import time
import datetime
from date_utils import translate_month
import logging
logger = logging.getLogger('bioportcontent')

class BlogView(BrowserView):
    def pretty_format_date(self, date):
        tool = getToolByName(self.context, 'portal_languages')
        current_language = tool.getLanguageBindings()[0]
        # The catalog stores a string to represent the date
        # we have to parse it
        try:
            year, month, day, m,m,m,m,m,m = time.strptime(date,"%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.error("Error formatting date %s" % date)
            return ''
        ts = getGlobalTranslationService()
        month_name = translate_month(month, current_language)
        weekday_index = datetime.date(year, month, day).weekday()
        # It looks like Plone's i18nl10n expects 0 to be a monday
        # while datetime's expects sunday. So we adjust it.
        weekday_index = (weekday_index + 1) % 7
        weekday_id = i18nl10n.weekdayname_msgid(weekday_index)
        weekday_name = ts.translate(domain='plonelocales', msgid=weekday_id,
                                    target_language=current_language)
        result = "%s %i %s" % (weekday_name, int(day), month_name)
        return result
