from typing import Dict, Any, Union
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.conf import settings


class SQLInjectionProtection:
    # SQL injection blacklist
    BLACKLIST = {
        # Basic SQL Commands
        "select", "insert", "update", "delete", "drop", "create", "alter", 
        "truncate", "execute", "exec", "declare",
        
        # SQL Comments
        "--", "/*", "*/", "#",
        
        # SQL Functions
        "char(", "nchar(", "varchar(", "nvarchar(", "cast(", "convert(",
        
        # System Tables
        "sysobjects", "syscolumns", "sysusers", "sysindexes",
        
        # Dangerous Keywords
        "union", "join", "substring", "information_schema",
        
        # Script Tags
        "<script", "</script>",
        
        # Special Characters
        "@@", ";" #, "'"
    }
    
    # Patterns that require exact matching
    EXACT_MATCH_PATTERNS = {
        "drop", "select", "insert", "delete", "update", "create", "alter"
    }
    
    # Error messages based on content type
    ERROR_MESSAGES = {
        'application/json': {
            'error': 'Suspicious activity detected. Do not try again.',
            'status': 403
        },
        'text/html': (
            '<html><body>'
            '<h1>Access Denied</h1>'
            '<p>Suspicious activity detected. Do not try again.</p>'
            '</body></html>'
        ),
        'default': 'Suspicious activity detected. Do not try again.'
    }

    @classmethod
    def get_excluded_paths(cls):
        """Get paths excluded from SQL injection checking"""
        return getattr(settings, 'SQL_INJECTION_EXCLUDED_PATHS', [])

    @classmethod
    def get_excluded_params(cls):
        """Get parameters excluded from SQL injection checking"""
        return getattr(settings, 'SQL_INJECTION_EXCLUDED_PARAMS', [])

    @staticmethod
    def clean_input(value: str) -> str:
        """Clean and normalize input for checking"""
        if not isinstance(value, str):
            value = str(value)
        return value.lower().strip()

    @classmethod
    def check_exact_match(cls, value: str) -> bool:
        """Check if value exactly matches any dangerous patterns"""
        cleaned = cls.clean_input(value)
        words = cleaned.split()
        return any(word in cls.EXACT_MATCH_PATTERNS for word in words)

    @classmethod
    def check_pattern_match(cls, value: str) -> bool:
        """Check if value contains any dangerous patterns"""
        cleaned = cls.clean_input(value)
        return any(pattern in cleaned for pattern in cls.BLACKLIST)

    @classmethod
    def check_string_for_sql(cls, value: str, param_name: str = None) -> bool:
        """Enhanced SQL injection check with logging"""
        if not value or len(value.strip()) == 0:
            return False
            
        # Skip excluded parameters
        if param_name and param_name in cls.get_excluded_params():
            return False

        # Perform both exact and pattern matching
        is_dangerous = cls.check_exact_match(value) or cls.check_pattern_match(value)
        
        if is_dangerous:
            return True
            
        return False

    @classmethod
    def check_sql_injection(cls, request: HttpRequest) -> bool:
        """Check request for SQL injection attempts"""
        # Skip excluded paths
        path = request.path.lstrip('/')
        if any(path.startswith(excluded) for excluded in cls.get_excluded_paths()):
            return False

        # Check GET parameters
        for key, value in request.GET.items():
            if cls.check_string_for_sql(value, key):
                return True

        # Check POST parameters
        for key, value in request.POST.items():
            if cls.check_string_for_sql(value, key):
                return True

        # Check cookies
        for key, value in request.COOKIES.items():
            if cls.check_string_for_sql(value, key):
                return True

        return False

    @classmethod
    def get_error_response(cls, request: HttpRequest):
        """Return appropriate error response based on content type"""
        content_type = request.headers.get('Accept', 'text/html')
        
        if 'application/json' in content_type:
            return JsonResponse(
                cls.ERROR_MESSAGES['application/json'],
                status=cls.ERROR_MESSAGES['application/json']['status']
            )
        elif 'text/html' in content_type:
            return HttpResponse(
                cls.ERROR_MESSAGES['text/html'],
                content_type='text/html',
                status=403
            )
        else:
            return HttpResponse(
                cls.ERROR_MESSAGES['default'],
                content_type='text/plain',
                status=403
            )

class SQLInjectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            is_injection = SQLInjectionProtection.check_sql_injection(request)
            if is_injection:
                return SQLInjectionProtection.get_error_response(request)
            
            return self.get_response(request)
            
        except Exception as e:
            return self.get_response(request)
