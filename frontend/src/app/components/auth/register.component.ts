// Visual refresh: renamed form fields/state while keeping registration flow and validation intact
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  signupForm: FormGroup;
  isSubmitting = false;
  formError = '';

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.signupForm = this.formBuilder.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  get controls() {
    return this.signupForm.controls;
  }

  passwordMatchValidator(form: FormGroup) {
    const passwordControl = form.get('password');
    const confirmControl = form.get('confirmPassword');

    if (passwordControl && confirmControl && passwordControl.value !== confirmControl.value) {
      confirmControl.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }

    return null;
  }

  submitRegistration(): void {
    if (this.signupForm.invalid) {
      return;
    }

    this.isSubmitting = true;
    this.formError = '';

    const { confirmPassword, ...userData } = this.signupForm.value;

    this.authService.register(userData).subscribe({
      next: () => {
        this.router.navigate(['/media']);
      },
      error: (error) => {
        this.formError = error.error?.message || 'Registration failed. Please try again.';
        this.isSubmitting = false;
      }
    });
  }
}
