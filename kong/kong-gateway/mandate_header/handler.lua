local plugin = {
    PRIORITY = 1000,
    VERSION = "0.1",
  }
  
  function plugin:init_worker()
  
    kong.log.debug("Mandate Header Plugin: init_worker")
  
  end
  
  
  function plugin:access(plugin_conf)
    kong.log.inspect(plugin_conf)
    local headers = kong.request.get_headers()[plugin_conf.request_header]
    if headers == nil then
      kong.response.exit(403, { message = "No " .. tostring(plugin_conf.request_header) .." header found in the request" })
    end
  end
  
  
  return plugin