import re,htmlentitydefs
 
def htmlentitydecode(s):
    # From: http://codeunivers.com/codes/python/decode_html_entities_unicode_characters
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[entity])
        return " "  # Unknown entity: We replace with a space.
    t = re.sub('&(%s);' % u'|'.join(htmlentitydefs.name2codepoint), entity2char, s)
 
    # Then convert numerical entities
    t = re.sub('&', "&amp;", t)
    #t = re.sub('[&#[\d];]', lambda x: unichr(int(x.group(1))), t)
    # Then convert hexa entities
    #re.sub('[&#x[\w];]', lambda x: unichr(int(x.group(1),16)), t)
    return t

remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')

def clean_xml(body):
    #Is not finished. Should clean XML below for parsing with lxml  
    return remove_re.sub('', htmlentitydecode(body))

bo = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:creativeCommons="http://backend.userland.com/creativeCommonsRssModule"
    xmlns:media="http://search.yahoo.com/mrss/"
    xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
    xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:blip="http://blip.tv/dtd/blip/1.0"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:amp="http://www.adobe.com/amp/1.0"
    xmlns:dcterms="http://purl.org/dc/terms"
    xmlns:gm="http://www.google.com/schemas/gm/1.1"
    xmlns:mediaad="http://blip.tv/dtd/mediaad/1.0"
>
<channel>
<title> - blip.tv</title>
<link>http://blip.tv</link>







<description>blip.tv</description>

<language>en-us</language>
<generator>http://blip.tv</generator>
<lastBuildDate>Mon, 11 Apr 2011 22:09:55 +0000</lastBuildDate>
<pubDate>Mon, 11 Apr 2011 22:09:55 +0000</pubDate>




<item>

  <guid isPermaLink="false">6EB32C4C-6488-11E0-829F-C098C64B7985</guid>

<link>http://blip.tv/file/5006677</link>
<title>Copii &#56167;hea?? &#56096;gr?dini?e</title>
<blip:user>unghenitv</blip:user>
<blip:userid>505433</blip:userid>
<blip:safeusername>ungheni</blip:safeusername>
<blip:show>UNGHENI.TV</blip:show>
<blip:showpage>http://www.ungheni.tv</blip:showpage>
<blip:picture>http://a.images.blip.tv/Unghenitv-picture961.png</blip:picture>
<blip:posts_id>5024503</blip:posts_id>
<blip:item_id>5006677</blip:item_id>
<blip:item_type>file</blip:item_type>
<blip:contentRating>TV-UN</blip:contentRating>
<blip:rating>0.0</blip:rating>
<blip:datestamp>2011-04-11T22:09:55Z</blip:datestamp>
<blip:language>English</blip:language>
<blip:adChannel></blip:adChannel>
<blip:recommendations>0</blip:recommendations>
<blip:recommendable>0</blip:recommendable>
<blip:core>0</blip:core>


<blip:adminRating>null</blip:adminRating>
<blip:runtime>123</blip:runtime>
<blip:embedLookup>hZJGgrLWWwI</blip:embedLookup>
<blip:embedUrl type="application/x-shockwave-flash">http://blip.tv/play/hZJGgrLWWwI</blip:embedUrl>

<wfw:commentRss>http://blip.tv/comments/?attached_to=post5024503&amp;skin=rss</wfw:commentRss>

<blip:thumbnail_src>Unghenitv-CopiiNgheaNGrdinie713-920.jpg</blip:thumbnail_src>
<blip:puredescription><![CDATA[La gr?dini?a &#132;Stelu?a&#148; din ora?ul Ungheni &#238;n s?lile pentru copii temperatura aerului abia se ridic? la 15 C, adic? cu 3 grade mai pu?in dec&#226;t prevede norma. Ca sa nu &#238;nghe?e, micu?ii stau cu hainele pe ei ?i cu c?ciulile pe cap.]]></blip:puredescription>
<blip:smallThumbnail>http://a.images.blip.tv/Unghenitv-CopiiNgheaNGrdinie713-920-469.jpg</blip:smallThumbnail>
<blip:license>Public Domain</blip:license>


<description>
<![CDATA[

<iframe src="http://blip.tv/play/hZJGgrLWWwI.html" width="480" height="414" frameborder="0" allowfullscreen></iframe><embed type="application/x-shockwave-flash" src="http://a.blip.tv/api.swf#hZJGgrLWWwI" style="display:none"></embed>
<br />

La gr?dini?a &#132;Stelu?a&#148; din ora?ul Ungheni &#238;n s?lile pentru copii temperatura aerului abia se ridic? la 15 C, adic? cu 3 grade mai pu?in dec&#226;t prevede norma. Ca sa nu &#238;nghe?e, micu?ii stau cu hainele pe ei ?i cu c?ciulile pe cap.

]]>
</description>

<comments>http://blip.tv/file/5006677</comments>



<category>Citizen Journalism</category>


<category>ungheni</category>

<category>ungheni.tv</category>

<category>copii</category>

<category>frig</category>


<pubDate>Mon, 11 Apr 2011 22:09:55 +0000</pubDate>
<enclosure url="http://blip.tv/file/get/Unghenitv-CopiiNgheaNGrdinie713.flv" length="14592028" type="video/flv" />

<itunes:keywords>ungheni, ungheni.tv, copii, frig</itunes:keywords>
<itunes:image>http://a.images.blip.tv/Unghenitv-CopiiNgheaNGrdinie713-920.jpg</itunes:image>

<media:keywords>ungheni, ungheni.tv, copii, frig</media:keywords>
<media:group>

<media:content url="http://blip.tv/file/get/Unghenitv-CopiiNgheaNGrdinie713.flv" type="video/x-flv" fileSize="14592028" isDefault="true" height="480" width="600" expression="full" blip:role="Source" blip:acodec="ffaac" blip:vcodec="ffh264">


    
            
                
<mediaad:content
    provider="freewheel"
    position="preroll"
    wgt="1.0" 
    pro="1.0"
    exc="0"
     was_blend="1" 
/>


            
                
<mediaad:content
    provider="scanscoutbranded"
    position="preroll"
    wgt="1.0" 
    pro="1.0"
    exc="0"
     was_blend="1" 
/>


            
            
                




            
            
                
    <mediaad:content
        provider="freewheel"
        position="overlay"
        start="5"
        duration="15"
        wgt="1.0" 
        pro="1.0"
        exc="0"
         was_blend="1"   
/>


            
                
    <mediaad:content
        provider="scanscout"
        position="overlay"
        start="5"
        duration="15"
        wgt="1.0" 
        pro="1.0"
        exc="0"
         was_blend="1"   
/>


            
                
    <mediaad:content
        provider="scanscoutbranded"
        position="overlay"
        start="5"
        duration="15"
        wgt="1.0" 
        pro="1.0"
        exc="0"
         was_blend="1"   
/>


            
            
                
    <mediaad:content
        provider="freewheel" 
        wgt="1.0" 
        pro="1.0"
        exc="0"
         was_blend="1" 
        position="postroll" />



            
                
    <mediaad:content
        provider="podaddies" 
        wgt="1.0" 
        pro="1.0"
        exc="0"
         was_blend="1" 
        position="postroll" />



            
        

</media:content>

</media:group>
<media:player url="http://blip.tv/file/5006677"><![CDATA[<iframe src="http://blip.tv/play/hZJGgrLWWwI.html" width="480" height="414" frameborder="0" allowfullscreen></iframe><embed type="application/x-shockwave-flash" src="http://a.blip.tv/api.swf#hZJGgrLWWwI" style="display:none"></embed>]]>
</media:player>




<media:title>Copii &#56167;hea?? &#56096;gr?dini?e</media:title>
<media:thumbnail url="http://a.images.blip.tv/Unghenitv-CopiiNgheaNGrdinie713-920.jpg" />







<creativeCommons:license>http://creativecommons.org/licenses/publicdomain/</creativeCommons:license>

  
  


</item>







</channel>
</rss>
"""

class LXMLAdapter(object):
    def __init__(self, miniNode):
        self.miniNode = miniNode
        
    def getAttribute(self, att_name):
        return  self.miniNode.attrib.get(att_name, None)
    
