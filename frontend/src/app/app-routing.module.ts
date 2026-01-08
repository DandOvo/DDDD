import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/auth/login.component';
import { RegisterComponent } from './components/auth/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { BodyMetricListComponent } from './components/body-metrics/body-metric-list.component';
import { WorkoutListComponent } from './components/workouts/workout-list.component';
import { NutritionListComponent } from './components/nutrition/nutrition-list.component';
import { ProgressPhotoListComponent } from './components/progress-photos/progress-photo-list.component';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'body-metrics',
    component: BodyMetricListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'workouts',
    component: WorkoutListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'nutrition',
    component: NutritionListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'progress-photos',
    component: ProgressPhotoListComponent,
    canActivate: [AuthGuard]
  },
  { path: '**', redirectTo: '/dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
