
# Menu Templates Directory

## Purpose
Contains navigation menu templates for the Barody Broject application. These templates provide responsive navigation components including main navigation bars, dropdown menus, and mobile-friendly menu structures for consistent site navigation.

## Contents
- `meno.html`: Main navigation menu template (likely should be "menu.html")
- `dropdown.html`: Dropdown menu component for secondary navigation items

## Usage

### Main Navigation Menu
```django
<!-- menu.html (or meno.html) -->
{% load static %}

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="{% url 'home' %}">
            <img src="{% static 'images/logo.png' %}" alt="Barody Broject" height="30">
            Barody Broject
        </a>
        
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav mr-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'home' %}">Home</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'articles_list' %}">Articles</a>
                </li>
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="categoriesDropdown" 
                       role="button" data-toggle="dropdown">
                        Categories
                    </a>
                    {% include "menu/dropdown.html" with items=categories %}
                </li>
            </ul>
            
            <ul class="navbar-nav">
                {% if user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" 
                           role="button" data-toggle="dropdown">
                            <i class="fas fa-user"></i> {{ user.username }}
                        </a>
                        <div class="dropdown-menu dropdown-menu-right">
                            <a class="dropdown-item" href="{% url 'profile' %}">
                                <i class="fas fa-user-circle"></i> Profile
                            </a>
                            <a class="dropdown-item" href="{% url 'account_email' %}">
                                <i class="fas fa-envelope"></i> Email Settings
                            </a>
                            <a class="dropdown-item" href="{% url 'mfa_dashboard' %}">
                                <i class="fas fa-shield-alt"></i> Security
                            </a>
                            <div class="dropdown-divider"></div>
                            <a class="dropdown-item" href="{% url 'account_logout' %}">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </div>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'account_login' %}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn btn-outline-light ml-2" href="{% url 'account_signup' %}">
                            Sign Up
                        </a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
```

### Dropdown Menu Component
```django
<!-- dropdown.html -->
<div class="dropdown-menu">
    {% for item in items %}
        {% if item.children %}
            <h6 class="dropdown-header">{{ item.title }}</h6>
            {% for child in item.children %}
                <a class="dropdown-item" href="{{ child.url }}">
                    {% if child.icon %}
                        <i class="{{ child.icon }}"></i>
                    {% endif %}
                    {{ child.title }}
                </a>
            {% endfor %}
            {% if not forloop.last %}
                <div class="dropdown-divider"></div>
            {% endif %}
        {% else %}
            <a class="dropdown-item" href="{{ item.url }}">
                {% if item.icon %}
                    <i class="{{ item.icon }}"></i>
                {% endif %}
                {{ item.title }}
                {% if item.badge %}
                    <span class="badge badge-{{ item.badge.type }} ml-auto">
                        {{ item.badge.text }}
                    </span>
                {% endif %}
            </a>
        {% endif %}
    {% endfor %}
</div>
```

### Mobile-Responsive Menu
```css
/* Menu styling for responsive navigation */
@media (max-width: 991.98px) {
    .navbar-collapse {
        background-color: rgba(0, 123, 255, 0.95);
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 0.375rem;
    }
    
    .navbar-nav .nav-link {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dropdown-menu {
        position: static;
        float: none;
        border: none;
        box-shadow: none;
        background-color: rgba(255, 255, 255, 0.1);
        margin-left: 1rem;
    }
}
```

### JavaScript Menu Enhancements
```javascript
// Enhanced menu functionality
document.addEventListener('DOMContentLoaded', function() {
    // Active page highlighting
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            
            // If in dropdown, show parent as active
            const dropdown = link.closest('.dropdown');
            if (dropdown) {
                dropdown.querySelector('.dropdown-toggle').classList.add('active');
            }
        }
    });
    
    // Dropdown hover effect on desktop
    if (window.innerWidth >= 992) {
        document.querySelectorAll('.dropdown').forEach(dropdown => {
            dropdown.addEventListener('mouseenter', function() {
                this.querySelector('.dropdown-menu').classList.add('show');
            });
            
            dropdown.addEventListener('mouseleave', function() {
                this.querySelector('.dropdown-menu').classList.remove('show');
            });
        });
    }
    
    // Search functionality
    const searchForm = document.getElementById('navbar-search');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = this.querySelector('input[name="q"]').value.trim();
            if (!query) {
                e.preventDefault();
                alert('Please enter a search term');
            }
        });
    }
});
```

### Menu Data Context
```python
# In context processors or views
def menu_context(request):
    """Provide menu data to templates"""
    
    categories = [
        {
            'title': 'News Categories',
            'children': [
                {'title': 'Politics', 'url': '/categories/politics/', 'icon': 'fas fa-landmark'},
                {'title': 'Technology', 'url': '/categories/tech/', 'icon': 'fas fa-laptop'},
                {'title': 'Sports', 'url': '/categories/sports/', 'icon': 'fas fa-football-ball'},
                {'title': 'Entertainment', 'url': '/categories/entertainment/', 'icon': 'fas fa-film'},
            ]
        },
        {
            'title': 'Special Features',
            'children': [
                {'title': 'AI Generated', 'url': '/ai-articles/', 'icon': 'fas fa-robot', 
                 'badge': {'type': 'info', 'text': 'New'}},
                {'title': 'Trending', 'url': '/trending/', 'icon': 'fas fa-fire'},
            ]
        }
    ]
    
    return {
        'categories': categories,
        'user_notifications': get_user_notifications(request.user) if request.user.is_authenticated else []
    }
```

## Container Configuration
- **Runtime**: Django template rendering with navigation context
- **Dependencies**: 
  - Bootstrap JavaScript and CSS for responsive components
  - FontAwesome icons for menu items
  - jQuery for dropdown and mobile menu functionality
- **Environment**: Integrated with Django URL routing and user authentication
- **Performance**: Template fragment caching for menu components

## Related Paths
- **Incoming**: 
  - Base template layout and structure
  - User authentication and authorization context
  - Application URL configuration and routing
  - Dynamic menu data from models or APIs
- **Outgoing**: 
  - Page navigation and routing
  - User authentication workflows
  - Search functionality and filtering
  - Mobile responsive layout systems
