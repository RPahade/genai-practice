import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ThemeService {
    private darkModeSubject = new BehaviorSubject<boolean>(true);
    public darkMode$ = this.darkModeSubject.asObservable();

    constructor() {
        // Check localStorage for saved preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.darkModeSubject.next(savedTheme === 'dark');
        }
        this.applyTheme(this.darkModeSubject.value);
    }

    toggleTheme() {
        const newTheme = !this.darkModeSubject.value;
        this.darkModeSubject.next(newTheme);
        this.applyTheme(newTheme);
        localStorage.setItem('theme', newTheme ? 'dark' : 'light');
    }

    private applyTheme(isDark: boolean) {
        if (isDark) {
            document.body.classList.add('dark-theme');
            document.body.classList.remove('light-theme');
        } else {
            document.body.classList.add('light-theme');
            document.body.classList.remove('dark-theme');
        }
    }

    get isDarkMode(): boolean {
        return this.darkModeSubject.value;
    }
}
