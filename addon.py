#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import os
import sys
import urllib2
import urlparse

import xml.etree.ElementTree

import buggalo

import xbmcgui
import xbmcaddon
import xbmcplugin

DATA_URL = 'http://webtv.metropol.dk/cat/345'

# TODO improve xpath expressions once script.module.elementtree is 1.3+

class SportenAddon(object):
    def showClips(self):
        doc = self.loadXml()
        for media in doc.findall('items/item'):
            title = media.findtext('title')
            thumbs = media.findall('thumbs/thumb')
            image = thumbs[len(thumbs) - 1].text
            xmlurl = media.findtext('xmlurl')

            infoLabels = dict()
            infoLabels['studio'] = ADDON.getAddonInfo('name')
            infoLabels['plot'] = media.findtext('desc')
            infoLabels['title'] = title
            infoLabels['aired'] = media.findtext('publisheddatetime')[0:10]
            infoLabels['year'] = int(media.findtext('publisheddatetime')[0:4])

            item = xbmcgui.ListItem(title, iconImage = image, thumbnailImage = image)
            item.setInfo('video', infoLabels)
            item.setProperty('Fanart_Image', image)
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(HANDLE, PATH + '?xmlurl=' + xmlurl, item)

        xbmcplugin.endOfDirectory(HANDLE)

    def playClip(self, xmlUrl):
        doc = self.loadXml(xmlUrl)
        if doc:
            server = doc.find('vurls').attrib.get('server')
            vurls = doc.findall('vurls/vurl')
            videoUrl = vurls[len(vurls) - 1].text

            item = xbmcgui.ListItem(path = server + videoUrl)
            xbmcplugin.setResolvedUrl(HANDLE, True, item)
        else:
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())

    def loadXml(self, url = DATA_URL):
#        try:
        u = urllib2.urlopen(url)
        response = u.read()
        u.close()
        doc = xml.etree.ElementTree.fromstring(response)
#        except Exception:
#            pass

        return doc

if __name__ == '__main__':
    ADDON = xbmcaddon.Addon()
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')
    FANART = os.path.join(ADDON.getAddonInfo('path'), 'fanart.jpg')

    buggalo.SUBMIT_URL = 'http://tommy.winther.nu/exception/submit.php'
    try:
        sporten = SportenAddon()
        if PARAMS.has_key('xmlurl'):
            sporten.playClip(PARAMS['xmlurl'][0])
        else:
            sporten.showClips()
    except Exception:
        buggalo.onExceptionRaised()
