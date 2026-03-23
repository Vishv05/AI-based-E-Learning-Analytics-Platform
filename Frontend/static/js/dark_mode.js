/* Dark Mode Toggle JavaScript
   Manages theme switching with localStorage persistence
*/

(function() {
  'use strict';

  // Theme class for managing dark/light mode
  class ThemeManager {
    constructor() {
      this.THEME_KEY = 'theme-preference';
      this.DARK_THEME = 'dark-mode';
      this.LIGHT_THEME = 'light-mode';
      this.OS_PREFERENCE_KEY = 'os-preference';
      
      this.init();
    }

    init() {
      // Check saved preference first
      let savedTheme = localStorage.getItem(this.THEME_KEY);
      
      if (savedTheme) {
        this.setTheme(savedTheme);
      } else {
        // Use system preference if no saved preference
        if (this.getSystemPreference()) {
          this.setTheme(this.DARK_THEME);
        } else {
          this.setTheme(this.LIGHT_THEME);
        }
      }
      
      this.createToggleButton();
      this.attachListeners();
    }

    getSystemPreference() {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    setTheme(theme) {
      if (theme === this.DARK_THEME) {
        document.body.classList.add(this.DARK_THEME);
        localStorage.setItem(this.THEME_KEY, this.DARK_THEME);
      } else {
        document.body.classList.remove(this.DARK_THEME);
        localStorage.setItem(this.THEME_KEY, this.LIGHT_THEME);
      }
      
      this.updateToggleButton();
    }

    toggleTheme() {
      const isDarkMode = document.body.classList.contains(this.DARK_THEME);
      this.setTheme(isDarkMode ? this.LIGHT_THEME : this.DARK_THEME);
    }

    createToggleButton() {
      // Check if button already exists
      if (document.getElementById('theme-toggle-btn')) {
        return;
      }

      const button = document.createElement('button');
      button.id = 'theme-toggle-btn';
      button.className = 'theme-toggle';
      button.setAttribute('title', 'Toggle dark mode (or use T key shortcut)');
      button.setAttribute('aria-label', 'Toggle theme');
      
      this.updateToggleButtonContent(button);
      
      document.body.appendChild(button);
      button.addEventListener('click', () => this.toggleTheme());
    }

    updateToggleButton() {
      const button = document.getElementById('theme-toggle-btn');
      if (button) {
        this.updateToggleButtonContent(button);
      }
    }

    updateToggleButtonContent(button) {
      const isDarkMode = document.body.classList.contains(this.DARK_THEME);
      button.innerHTML = isDarkMode ? '☀️' : '🌙';
    }

    attachListeners() {
      // Keyboard shortcut: T key to toggle theme
      document.addEventListener('keydown', (e) => {
        if (e.key === 't' || e.key === 'T') {
          // Don't toggle if user is typing in an input field
          if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            this.toggleTheme();
          }
        }
      });

      // Listen for system preference changes
      if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
          if (!localStorage.getItem(this.THEME_KEY)) {
            this.setTheme(e.matches ? this.DARK_THEME : this.LIGHT_THEME);
          }
        });
      }
    }

    getTheme() {
      return document.body.classList.contains(this.DARK_THEME) ? this.DARK_THEME : this.LIGHT_THEME;
    }

    prefersSystemTheme() {
      return !localStorage.getItem(this.THEME_KEY);
    }
  }

  // Initialize theme manager when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.themeManager = new ThemeManager();
    });
  } else {
    window.themeManager = new ThemeManager();
  }
})();

// API for other scripts to interact with theme
window.Theme = {
  toggle: function() {
    if (window.themeManager) {
      window.themeManager.toggleTheme();
    }
  },
  
  set: function(theme) {
    if (window.themeManager) {
      window.themeManager.setTheme(theme);
    }
  },
  
  get: function() {
    if (window.themeManager) {
      return window.themeManager.getTheme();
    }
    return 'light-mode';
  },
  
  isDark: function() {
    return this.get() === 'dark-mode';
  },
  
  isLight: function() {
    return this.get() === 'light-mode';
  }
};
