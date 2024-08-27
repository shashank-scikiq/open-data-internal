
import logging
import functools
import os
from rest_framework.response import Response
from rest_framework.request import Request
import uuid
import re
from django.views.generic import View
import sys
import apps.utils.constant as constant

class NotFoundException(Exception):
    pass

def responsejson(data, msg, status):
    """Helper function to format the response JSON."""
    return {
        'status': status,
        'data': data,
        'message': msg
    }



def responsejson1(status, msg="", data=[], type="json", request_id=-1):
    if not isinstance(status, int):
        return {"error": True, "msg": "Internal Server Error", "status": 500, "data": data, "type": type,
                "request_id": request_id}

    if isinstance(msg, dict) and 'msg_details' in msg:
        msg_str = msg
    elif isinstance(msg, dict):
        msg_str = ", ".join([f"{k} ({v[0]})" for k, v in msg.items()])
    elif isinstance(msg, str):
        msg_str = msg
    else:
        return {"error": True, "msg": "Internal Server Error", "status": 500, "data": data, "type": type,
                "request_id": request_id}

    if status == 200 or status == 201:
        return {"error": False, "msg": msg_str, "status": status, "data": data, "type": type, "request_id": request_id}
    elif status == 400:
        return {"error": True, "msg": msg_str, "status": status, "data": data, "type": type, "request_id": request_id}
    elif status == 401:
        return {"error": True, "msg": msg_str or "Unauthorized", "status": status, "data": data, "type": type,
                "request_id": request_id}
    elif status == 403:
        return {"error": True, "msg": msg_str or "Forbidden", "status": status, "data": data, "type": type,
                "request_id": request_id}
    elif status == 404:
        return {"error": True, "msg": msg_str or "Not Found", "status": status, "data": data, "type": type,
                "request_id": request_id}
    elif status == 422:
        return {"error": True, "msg": msg_str or "Unprocessable Entity", "status": status, "data": data, "type": type,
                "request_id": request_id}
    else:
        return {"error": True, "msg": msg_str, "status": status, "data": data, "type": type, "request_id": request_id}


# Function to configure logging based on environment variables
def configure_logging():
    logger = logging.getLogger()  # Get the root logger

    log_level = constant.LOG_LEVEL
    enable_console_log = constant.enable_console_log
    if log_level in ('DEBUG', 'INFO'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Stream Handler for STDOUT
    if enable_console_log:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def exceptionAPI(logger, msg='Unable to process'):
    """
    A decorator that wraps the passed-in function and logs
    exceptions should one occur

    @param logger: The logging object
    @param msg: The logging object
    """

    def decorator(func):
        @functools.wraps(func)
        def getParams(e, *args, **kwargs):
            params = {"function": func.__doc__}

            for arg in args:
                if isinstance(arg, View):
                    arg.request_id = str(uuid.uuid4())
                    params["request_id"] = arg.request_id
                if isinstance(arg, Request):
                    for key in arg.GET.keys():
                        params[key] = arg.GET[key]

                    if arg.data:
                        params["body"] = arg.data

                    if arg.headers:
                        params["headers"] = arg.headers

            for key, value in kwargs.items():
                params[key] = value

            if e:
                params["error"] = str(e)
            return params

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                params = getParams(None, *args, **kwargs)
                logger.info("Start Function : " + func.__doc__, extra=params)

                res = func(*args, **kwargs)
                params["response"] = res
                logger.info("End Function : " + func.__doc__, extra=params)
                return res
            except NotFoundException as e:
                # log the exception and return a 404 response
                msg_dict = {'msg': msg, 'msg_details': remove_html_tags(str(e))}
                logger.exception("Exception in API call : " + func.__doc__ + " " + str(e),
                                 extra=getParams(e, *args, **kwargs))
                return Response(responsejson(data='', msg=msg_dict, status=404), status=404)

            except Exception as e:
                # log the exception and return a 500 response
                msg_dict = {'msg': msg, 'msg_details': remove_html_tags(str(e))}
                logger.exception("Exception in API call : " + func.__doc__ + " " + str(e),
                                 extra=getParams(e, *args, **kwargs))
                return Response(responsejson(data='', msg=msg_dict, status=500), status=500)

        return wrapper

    return decorator


def remove_html_tags(text):
    clean = re.compile(r'"<.*?>"')
    return re.sub(clean, '', text)


# Decorator for logging function calls
def log_function_call(logger):

    def decorator(func):
        @functools.wraps(func)
        def getParams(e, *args, **kwargs) :
            params = {}
            params["function"] = func.__name__

            if len(args) == 1 :
                for arg in args:
                    if isinstance(arg, (str,int)) :
                        params["key"] = arg

            for key, value in kwargs.items():
                if isinstance(value, str) or isinstance(value, int) :
                    params[key] = value

            if e :
                params["error"] = str(e)
            return params

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info("Start Function : " + func.__name__)
                if logger.getEffectiveLevel() == logging.DEBUG:
                    logger.debug(func.__name__, extra=getParams(None, *args, **kwargs))

                res = func(*args, **kwargs)
                logger.info("End Function : " + func.__name__)
            except Exception as e:
                # log the exception
                logger.exception("Exception in function[" + func.__name__ + "] call.",
                                 extra=getParams(e, *args, **kwargs))
                raise
                # re-raise the exception
            return res

        return wrapper
    return decorator


ondcLogger = configure_logging()
