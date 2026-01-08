// Visual refresh: renamed form/state fields while keeping login logic intact
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  signinForm: FormGroup;
  isSubmitting = false;
  formError = '';
  redirectUrl: string;

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.signinForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.redirectUrl = this.route.snapshot.queryParams['returnUrl'] || '/media';
  }

  get controls() {
    return this.signinForm.controls;
  }

  submitCredentials(): void {
    if (this.signinForm.invalid) {
      return;
    }

    this.isSubmitting = true;
    this.formError = '';

    this.authService.login(this.signinForm.value).subscribe({
      next: () => {
        this.router.navigate([this.redirectUrl]);
      },
      error: (error) => {
        this.formError = error.error?.message || 'Login failed. Please check your credentials.';
        this.isSubmitting = false;
      }
    });
  }
}
