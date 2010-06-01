#!/usr/bin/ruby

require 'cgi'
require 'logger'

@logger = Logger.new('widget-demo.log', 5, 512000)
@widget_subdomain = ENV["HTTP_HOST"].split('.')[0]

if (@widget_subdomain == "mswidgetdev")
  @site_subdomain = "mirosubsdev"
else
  @site_subdomain = "mirosubsstaging"
end

begin
  @params = CGI::parse(ENV["QUERY_STRING"])

  if (@params["video_url"].length > 0)
    @js_query_string = "video_url=#{@params['video_url'][0]}"
  elsif (@params["youtube_videoid"].length > 0)
    @js_query_string = "youtube_videoid=#{@params['youtube_videoid'][0]}"
  else
    @js_query_string = "video_id=${@params['video_id'][0]}"
  end

  if (@params["null"].length > 0)
    @js_query_string = "#{@js_query_string}&null"
  end

  if (@params['debug_js'].length > 0)
    @js_query_string = "#{@js_query_string}&debug_js"
  end

  if (@params['autoplay'].length > 0)
    @js_query_string = "#{@js_query_string}&autoplay=#{@params['autoplay'][0]}"
  end

  @logger.info "called for #{@js_query_string}"

  cgi = CGI.new('html4')

  cgi.out() do
    cgi.html() do
      cgi.body() do
        cgi.div {  
          "<script src=\"http://#{@site_subdomain}.8planes.com/embed_widget.js?#{@js_query_string}\"></script>"
        } + 
        cgi.div {
          "<img src='/media/test.png' alt='some stupid image'/>"
        }
      end
    end
  end
rescue
  @logger.error $!
end
