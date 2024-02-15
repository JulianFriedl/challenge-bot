import logging

from colorlog import ColoredFormatter

def setup_logging(to_file=False):
    log_format = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    log_level = logging.INFO  # Set to DEBUG for verbose logging

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    if to_file:
        # Configure logging to write to a file
        logging.basicConfig(filename='app.log',
                            filemode='w',  # 'w' for overwrite, 'a' for append
                            format=log_format,
                            level=log_level)
    else:
        # Configure logging to output to console and Define a colored formatter
        
        colored_formatter = ColoredFormatter(
            "\033[1m\033[90m%(asctime)s\033[0m "  # ANSI escape code for dark grey
            "\033[1m%(log_color)s%(levelname)-8s%(reset)s\033[0m "
            "%(purple)s%(module)s%(reset)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white'
            },
            secondary_log_colors={
                'message': {
                    'DEBUG': 'white',
                    'INFO': 'white',
                    'WARNING': 'white',
                    'ERROR': 'white',
                    'CRITICAL': 'white'
                },
                'module': {
                    'DEBUG': 'purple',
                    'INFO': 'purple',
                    'WARNING': 'purple',
                    'ERROR': 'purple',
                    'CRITICAL': 'purple'
                }
            },
            style='%'
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)

