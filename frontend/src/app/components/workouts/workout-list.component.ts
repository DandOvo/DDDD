import { Component, OnInit } from '@angular/core';
import { WorkoutService } from '../../services/workout.service';
import { Workout } from '../../models/workout.model';

@Component({
  selector: 'app-workout-list',
  templateUrl: './workout-list.component.html',
  styleUrls: ['./workout-list.component.css']
})
export class WorkoutListComponent implements OnInit {
  workouts: Workout[] = [];
  loading = true;
  page = 1;
  pageSize = 20;
  total = 0;
  showForm = false;
  formData = {
    workoutType: '',
    duration: null as number | null,
    distance: null as number | null,
    intensity: '',
    notes: ''
  };

  constructor(private workoutService: WorkoutService) {}

  ngOnInit() {
    this.loadWorkouts();
  }

  loadWorkouts() {
    this.loading = true;
    this.workoutService.getList(this.page, this.pageSize).subscribe({
      next: (response) => {
        this.workouts = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Failed to load workouts', error);
        this.loading = false;
      }
    });
  }

  deleteWorkout(id: string) {
    if (confirm('确定要删除这条记录吗？')) {
      this.workoutService.delete(id).subscribe({
        next: () => this.loadWorkouts(),
        error: (error) => alert('删除失败')
      });
    }
  }

  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.resetForm();
    }
  }

  resetForm() {
    this.formData = {
      workoutType: '',
      duration: null,
      distance: null,
      intensity: '',
      notes: ''
    };
  }

  submitForm() {
    if (!this.formData.workoutType || !this.formData.duration) {
      alert('请填写运动类型和时长');
      return;
    }

    const now = new Date();
    const durationInSeconds = (this.formData.duration || 0) * 60;
    const endTime = new Date(now.getTime() + durationInSeconds * 1000);

    const data: any = {
      workoutType: this.formData.workoutType,
      startTime: now.toISOString(),
      endTime: endTime.toISOString(),
      duration: durationInSeconds
    };

    if (this.formData.distance) data.distance = this.formData.distance;
    if (this.formData.intensity) data.intensity = this.formData.intensity;
    if (this.formData.notes) data.notes = this.formData.notes;

    this.workoutService.create(data).subscribe({
      next: () => {
        this.showForm = false;
        this.resetForm();
        this.loadWorkouts();
      },
      error: (error) => {
        console.error('Failed to create workout', error);
        alert('添加失败');
      }
    });
  }
}
