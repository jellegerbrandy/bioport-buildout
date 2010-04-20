import datetime
from date_utils import translate_month
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PageTemplates.GlobalTranslationService import getGlobalTranslationService
from zope.interface import Interface

class BioportcontentUtils(BrowserView):
    def born_today_portlet_title(self):
        now = datetime.datetime.now()
        month_index, day = now.month, now.day
        tool = getToolByName(self.context, 'portal_languages')
        current_language = tool.getLanguageBindings()[0]
        month_name = translate_month(month_index, current_language)
        ts = getGlobalTranslationService()
        if current_language == 'nl':
            title = "Op %(day)i %(month_name)s geboren"
        else:
            title = "Born on %(month_name)s %(day)i"
        return title % locals()

class IBioportcontentUtils(Interface):
    def born_today_portlet_title():
        "Get the translated title for the born today portlets"



def set_http_redirects(context):
    from plone.app.redirector.interfaces import IRedirectionStorage
    from zope.component import queryUtility

    portal = context.getSite()
    rootpath = '/'.join(portal.getPhysicalPath() + ('nl',))
    storage = queryUtility(IRedirectionStorage)
    # clean up the redirection utility
    #[storage.destroy(a) for a in tuple(storage._rpaths.keys())]
    paths = (
                ('/collecties', '/about/collecties'),
                ('/redactieraad', '/about/redactieraad'),
                ('/instellingen', '/about/instellingen'),
                ('/stichting', '/about/stichting'),
                ('/colofon', '/about/colofon'),
                ('/biodes', '/about/biodes'),
        # the following are commented out to remind me that they are redundant:
        # the redirection engine checks for parents too
#                ('/biodes/beschrijving', '/about/biodes/beschrijving'),
#                ('/biodes/persoonsnaam', '/about/biodes/persoonsnaam'),
#                ('/biodes/schemas', '/about/biodes/schemas'),
#                ('/biodes/voorbeelden', '/about/biodes/voorbeelden'),
            )
    for old_path, new_path in paths:
        storage.add(rootpath + old_path, rootpath + new_path)

