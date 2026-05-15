import logging

import logtail


logger = logging.getLogger("fastship")
logger.setLevel(logging.INFO)

logtail_handler = logtail.LogtailHandler(
    source_token="nGkuoaaLJEhUovfYLw1VSSv2",
    host="s2441740.eu-fsn-3.betterstackdata.com",
)

logtail_handler.setFormatter(
    logging.Formatter(
        "[%(levelname)s]: %(message)s",
    ),
)
logger.addHandler(logtail_handler)
