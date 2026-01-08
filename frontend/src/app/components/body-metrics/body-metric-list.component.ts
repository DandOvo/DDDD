import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { BodyMetricService } from '../../services/body-metric.service';
import { BodyMetric } from '../../models/body-metric.model';

@Component({
  selector: 'app-body-metric-list',
  templateUrl: './body-metric-list.component.html',
  styleUrls: ['./body-metric-list.component.css']
})
export class BodyMetricListComponent implements OnInit {
  metrics: BodyMetric[] = [];
  loading = true;
  page = 1;
  pageSize = 20;
  total = 0;
  showForm = false;
  formData = {
    weight: null as number | null,
    bodyFatPercentage: null as number | null,
    muscleMass: null as number | null,
    notes: ''
  };

  constructor(
    private bodyMetricService: BodyMetricService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadMetrics();
  }

  loadMetrics() {
    this.loading = true;
    this.bodyMetricService.getList(this.page, this.pageSize).subscribe({
      next: (response) => {
        this.metrics = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Failed to load body metrics', error);
        this.loading = false;
      }
    });
  }

  deleteMetric(id: string) {
    if (confirm('确定要删除这条记录吗？')) {
      this.bodyMetricService.delete(id).subscribe({
        next: () => {
          this.loadMetrics();
        },
        error: (error) => {
          console.error('Failed to delete metric', error);
          alert('删除失败');
        }
      });
    }
  }

  getBmiClass(bmi?: number): string {
    if (!bmi) return '';
    if (bmi < 18.5) return 'text-blue-600'; // 偏瘦
    if (bmi < 25) return 'text-green-600'; // 正常
    if (bmi < 30) return 'text-yellow-600'; // 偏胖
    return 'text-red-600'; // 肥胖
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.resetForm();
    }
  }

  resetForm() {
    this.formData = {
      weight: null,
      bodyFatPercentage: null,
      muscleMass: null,
      notes: ''
    };
  }

  submitForm() {
    // 验证数值范围
    if (this.formData.weight && (this.formData.weight < 20 || this.formData.weight > 300)) {
      alert('体重必须在 20-300 kg 范围内');
      return;
    }
    if (this.formData.bodyFatPercentage && (this.formData.bodyFatPercentage < 0 || this.formData.bodyFatPercentage > 100)) {
      alert('体脂率必须在 0-100% 范围内');
      return;
    }
    if (this.formData.muscleMass && (this.formData.muscleMass < 10 || this.formData.muscleMass > 150)) {
      alert('肌肉量必须在 10-150 kg 范围内');
      return;
    }

    const data: any = {
      recordedAt: new Date().toISOString()
    };

    if (this.formData.weight) data.weight = this.formData.weight;
    if (this.formData.bodyFatPercentage) data.bodyFatPercentage = this.formData.bodyFatPercentage;
    if (this.formData.muscleMass) data.muscleMass = this.formData.muscleMass;
    if (this.formData.notes) data.notes = this.formData.notes;

    this.bodyMetricService.create(data).subscribe({
      next: () => {
        this.showForm = false;
        this.resetForm();
        this.loadMetrics();
      },
      error: (error) => {
        console.error('Failed to create body metric', error);
        alert('添加失败');
      }
    });
  }
}
