"""
Django settings for barodybroject project.

Generated by 'django-admin startproject' using Django 4.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# Determine whether we're in production, as this will affect many settings.
prod = bool(os.environ.get("RUNNING_IN_PRODUCTION", False))

if not prod:  # Running in a Test/Development environment
    DEBUG = True  # SECURITY WARNING: don't run with debug turned on in production!
    DEFAULT_SECRET = "insecure-secret-key"

    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
    ]
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8000",
    ]

else:  # Running in a Production environment
    DEBUG = True  # SECURITY WARNING: don't run with debug turned on in production!
    DEFAULT_SECRET = None
    ALLOWED_HOSTS = [
        os.environ["CONTAINER_APP_NAME"] + "." + os.environ["CONTAINER_APP_ENV_DNS_SUFFIX"],
    ]
    CSRF_TRUSTED_ORIGINS = [
        "https://" + os.environ["CONTAINER_APP_NAME"] + "." + os.environ["CONTAINER_APP_ENV_DNS_SUFFIX"],
    ]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECRET_KEY = 'django-insecure-9=woki=bii5gfdzfb3igh$qcxb=i+-u+!c58xl76x1tk)gaqd3'

SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_SECRET)


# Application definition

INSTALLED_APPS = [

    # Django core default apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    "django.contrib.humanize",
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Allauth apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.socialaccount.providers.github",
    "allauth.usersessions",

    # Django CMS base apps
    'djangocms_admin_style',
    'djangocms_alias',
    'djangocms_versioning',
    'djangocms_text_ckeditor',

    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'filer',
    'easy_thumbnails',
    'djangocms_frontend',
    'djangocms_frontend.contrib.accordion',
    'djangocms_frontend.contrib.alert',
    'djangocms_frontend.contrib.badge',
    'djangocms_frontend.contrib.card',
    'djangocms_frontend.contrib.carousel',
    'djangocms_frontend.contrib.collapse',
    'djangocms_frontend.contrib.content',
    'djangocms_frontend.contrib.grid',
    'djangocms_frontend.contrib.icon',
    'djangocms_frontend.contrib.image',
    'djangocms_frontend.contrib.jumbotron',
    'djangocms_frontend.contrib.link',
    'djangocms_frontend.contrib.listgroup',
    'djangocms_frontend.contrib.media',
    'djangocms_frontend.contrib.navigation',
    'djangocms_frontend.contrib.tabs',
    'djangocms_frontend.contrib.utilities',

    # API and REST Framework
    'rest_framework', # Add this line to include the rest_framework app in the project

    # Baroydy Broject apps
    'parodynews',  # Add this line to include the app in the project

    # Third-party apps
    'django_json_widget',  # Add this line to include the JSON widget app in the project
    'markdownify',  # Add this line to include the markdownify app in the project
    'martor',  # Add this line to include the martor app in the project
    'import_export',  # Add this line to include the import_export app in the project

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.utils.ApphookReloadMiddleware',  # Add this middleware
    'django.middleware.locale.LocaleMiddleware',  # Corrected middleware path
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'barodybroject.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'parodynews' /'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'parodynews.context_processors.footer_items',  # Add this line to include the footer_items context processor
                'django.template.context_processors.static',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'barodybroject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

db_options = {}
if ssl_mode := os.environ.get("POSTGRES_SSL"):
    db_options = {"sslmode": ssl_mode}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.environ.get("POSTGRES_DATABASE"),
#         "USER": os.environ.get("POSTGRES_USERNAME"),
#         "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
#         "HOST": os.environ.get("POSTGRES_HOST"),
#         "PORT": os.environ.get("POSTGRES_PORT", 5432),
#         "OPTIONS": db_options,
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        "OPTIONS": {
            "min_length": 6,
        },
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by email
    'allauth.account.auth_backends.AuthenticationBackend',
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
ACCOUNT_LOGIN_BY_CODE_ENABLED = True

MFA_SUPPORTED_TYPES = [
    "webauthn",
    "totp",
    "recovery_codes",
]
MFA_PASSKEY_LOGIN_ENABLED = False
MFA_PASSKEY_SIGNUP_ENABLED = False

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': [
            'read:user',
        ],
        'VERIFIED_EMAIL': True,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    # ("de", "German"),
    # ("fr", "French"),
    # Add other languages if needed
]

CMS_CONFIRM_VERSION4 = True

CMS_TEMPLATES = [
    ("base.html", _("Base Template")),
    ('parodynews/cms.html', 'CMS Template'),
    # ...existing templates...
]

CMS_PLACEHOLDERS = [
    ('content', 'Content'),
    # Add other placeholders if necessary
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'index'  # Redirect users to a 'home' page defined in your urls.py
LOGOUT_REDIRECT_URL = 'index'

STATIC_URL = '/static/'
# Add your static files directory
STATICFILES_DIRS = [
    BASE_DIR / "assets",
    BASE_DIR / "_site/assets",
    # Add other directories if needed
]

# Define STATIC_ROOT for collectstatic
STATIC_ROOT = BASE_DIR / "static"

# Post Root - where generated post files are stored

PAGES_DIR = BASE_DIR / "pages"
POST_DIR = PAGES_DIR / "_posts"

CSRF_COOKIE_HTTPONLY = False


X_FRAME_OPTIONS = "SAMEORIGIN"

SITE_ID = 1

TEXT_INLINE_EDITING = True

DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True

# CKEditor settings
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}


# Choices are: "semantic", "bootstrap"
MARTOR_THEME = 'bootstrap'

# Global martor settings
# Input: string boolean, `true/false`
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',        # to enable/disable emoji icons.
    'imgur': 'true',        # to enable/disable imgur/custom uploader.
    'mention': 'false',     # to enable/disable mention
    'jquery': 'true',       # to include/revoke jquery (require for admin default django)
    'living': 'false',      # to enable/disable live updates in preview
    'spellcheck': 'false',  # to enable/disable spellcheck in form textareas
    'hljs': 'true',         # to enable/disable hljs highlighting in preview
}

# To show the toolbar buttons
MARTOR_TOOLBAR_BUTTONS = [
    'bold', 'italic', 'horizontal', 'heading', 'pre-code',
    'blockquote', 'unordered-list', 'ordered-list',
    'link', 'image-link', 'image-upload', 'emoji',
    'direct-mention', 'toggle-maximize', 'help'
]

# To setup the martor editor with title label or not (default is False)
MARTOR_ENABLE_LABEL = False

# Disable admin style when using custom admin interface e.g django-grappelli (default is True)
MARTOR_ENABLE_ADMIN_CSS = False

# Imgur API Keys
MARTOR_IMGUR_CLIENT_ID = 'your-client-id'
MARTOR_IMGUR_API_KEY   = 'your-api-key'

# Markdownify
MARTOR_MARKDOWNIFY_FUNCTION = 'martor.utils.markdownify' # default
MARTOR_MARKDOWNIFY_URL = '/martor/markdownify/' # default

# Delay in milliseconds to update editor preview when in living mode.
MARTOR_MARKDOWNIFY_TIMEOUT = 0 # update the preview instantly
# or:
MARTOR_MARKDOWNIFY_TIMEOUT = 1000 # default

# Markdown extensions (default)
MARTOR_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
    'markdown.extensions.fenced_code',
    'markdown.extensions.sane_lists',

    # Custom markdown extensions.
    'martor.extensions.urlize',
    'martor.extensions.del_ins',      # ~~strikethrough~~ and ++underscores++
    'martor.extensions.mention',      # to parse markdown mention
    'martor.extensions.emoji',        # to parse markdown emoji
    'martor.extensions.mdx_video',    # to parse embed/iframe video
    'martor.extensions.escape_html',  # to handle the XSS vulnerabilities
    "martor.extensions.mdx_add_id",  # to parse id like {#this_is_id}
]

# Markdown Extensions Configs
MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}

# Markdown urls
MARTOR_UPLOAD_URL = '' # Completely disable the endpoint
# or:
MARTOR_UPLOAD_URL = '/martor/uploader/' # default

MARTOR_SEARCH_USERS_URL = '' # Completely disables the endpoint
# or:
MARTOR_SEARCH_USERS_URL = '/martor/search-user/' # default

# Markdown Extensions
# MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://www.webfx.com/tools/emoji-cheat-sheet/graphics/emojis/'     # from webfx
MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://github.githubassets.com/images/icons/emoji/'                  # default from github
# or:
MARTOR_MARKDOWN_BASE_EMOJI_URL = ''  # Completely disables the endpoint
MARTOR_MARKDOWN_BASE_MENTION_URL = 'https://python.web.id/author/'                                      # please change this to your domain

# If you need to use your own themed "bootstrap" or "semantic ui" dependency
# replace the values with the file in your static files dir
# MARTOR_ALTERNATIVE_JS_FILE_THEME = "test-themed/semantic.min.js"   # default None
# MARTOR_ALTERNATIVE_CSS_FILE_THEME = "test-themed/semantic.min.css" # default None
# MARTOR_ALTERNATIVE_JQUERY_JS_FILE = "jquery/dist/jquery.min.js"        # default None

# URL schemes that are allowed within links
ALLOWED_URL_SCHEMES = [
    "file", "ftp", "ftps", "http", "https", "irc", "mailto",
    "sftp", "ssh", "tel", "telnet", "tftp", "vnc", "xmpp",
]

# https://gist.github.com/mrmrs/7650266
ALLOWED_HTML_TAGS = [
    "a", "abbr", "b", "blockquote", "br", "cite", "code", "command",
    "dd", "del", "dl", "dt", "em", "fieldset", "h1", "h2", "h3", "h4", "h5", "h6",
    "hr", "i", "iframe", "img", "input", "ins", "kbd", "label", "legend",
    "li", "ol", "optgroup", "option", "p", "pre", "small", "span", "strong",
    "sub", "sup", "table", "tbody", "td", "tfoot", "th", "thead", "tr", "u", "ul"
]

# https://github.com/decal/werdlists/blob/master/html-words/html-attributes-list.txt
ALLOWED_HTML_ATTRIBUTES = [
    "alt", "class", "color", "colspan", "datetime",  # "data",
    "height", "href", "id", "name", "reversed", "rowspan",
    "scope", "src", "style", "title", "type", "width"
]