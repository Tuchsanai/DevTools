local typedefs = require "kong.db.schema.typedefs"


local PLUGIN_NAME = "mandate_header"


local schema = {
  name = PLUGIN_NAME,
  fields = {
    { consumer = typedefs.no_consumer },
    { protocols = typedefs.protocols_http },
    { config = {
        type = "record",
        fields = {
          { request_header = typedefs.header_name {
              required = true,
              default = "accesstoken" } }
        },
        entity_checks = {
          { at_least_one_of = { "request_header" }, },
          { distinct = { "request_header"} },
        },
      },
    },
  },
}

return schema