require 'cgi'
require 'logger'

@logger = Logger.new('widget-demo.log', 5, 512000)

begin
  @params = CGI::parse(ENV["QUERY_STRING"])

  if (@params["video_url"] != nil)
    @js_query_string = "video_url=#{@params['video_url']}"
  else
    @js_query_string = "youtube_id=#{@params['youtube_id']}"
  end

  if (@params["null"] != nil)
    @js_query_string = "#{@js_query_string}&null"
  end

  @logger.info "called for #{@js_query_string}"

  cgi = CGI.new('html4')

  cgi.out() do
    cgi.html() do
      cgi.body() do
       cgi.h1 { 'A video for you!' } +
       cgi.div {  
          "<script src=\"http://mirosubs.pybrew.com/embed_widget.js?#{@js_query_string}\"></script>"
       }
      end
    end
  end
rescue
  @logger.error $!
end
