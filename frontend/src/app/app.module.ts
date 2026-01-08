import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { NgApexchartsModule } from 'ng-apexcharts';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

// Auth Components
import { LoginComponent } from './components/auth/login.component';
import { RegisterComponent } from './components/auth/register.component';

// Shared Components
import { NavbarComponent } from './components/shared/navbar.component';
import { FooterComponent } from './components/shared/footer.component';

// Feature Components
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { BodyMetricListComponent } from './components/body-metrics/body-metric-list.component';
import { WorkoutListComponent } from './components/workouts/workout-list.component';
import { NutritionListComponent } from './components/nutrition/nutrition-list.component';
import { ProgressPhotoListComponent } from './components/progress-photos/progress-photo-list.component';

// Services
import { AuthService } from './services/auth.service';
import { AuthInterceptor } from './services/auth.interceptor';
import { BodyMetricService } from './services/body-metric.service';
import { WorkoutService } from './services/workout.service';
import { NutritionService } from './services/nutrition.service';
import { ProgressPhotoService } from './services/progress-photo.service';
import { DashboardService } from './services/dashboard.service';

// Guards
import { AuthGuard } from './guards/auth.guard';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    RegisterComponent,
    NavbarComponent,
    FooterComponent,
    DashboardComponent,
    BodyMetricListComponent,
    WorkoutListComponent,
    NutritionListComponent,
    ProgressPhotoListComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    NgApexchartsModule
  ],
  providers: [
    AuthService,
    BodyMetricService,
    WorkoutService,
    NutritionService,
    ProgressPhotoService,
    DashboardService,
    AuthGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
