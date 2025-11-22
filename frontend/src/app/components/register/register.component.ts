import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-register',
    templateUrl: './register.component.html',
    styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
    registerForm!: FormGroup;
    loading = false;
    submitted = false;
    error = '';

    constructor(
        private formBuilder: FormBuilder,
        private router: Router,
        private authService: AuthService
    ) {
        // redirect to home if already logged in
        if (this.authService.currentUserValue && this.authService.currentUserValue.access_token) {
            this.router.navigate(['/']);
        }
    }

    ngOnInit() {
        this.registerForm = this.formBuilder.group({
            email: ['', Validators.required],
            password: ['', [Validators.required, Validators.minLength(6)]]
        });
    }

    // convenience getter for easy access to form fields
    get f() { return this.registerForm.controls; }

    onSubmit() {
        this.submitted = true;
        console.log('Register form submitted');

        // stop here if form is invalid
        if (this.registerForm.invalid) {
            console.log('Register form invalid', this.registerForm.errors);
            return;
        }

        console.log('Registering user...', this.f['email'].value);

        this.loading = true;
        this.authService.register(this.f['email'].value, this.f['password'].value)
            .pipe(first())
            .subscribe(
                data => {
                    this.router.navigate(['/login'], { queryParams: { registered: true } });
                },
                error => {
                    this.error = error.error?.detail || error.statusText || 'An error occurred';
                    this.loading = false;
                });
    }
}
