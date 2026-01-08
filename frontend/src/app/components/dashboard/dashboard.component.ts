import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { DashboardOverview } from '../../models/dashboard.model';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  overview?: DashboardOverview;
  loading = true;
  error: string | null = null;

  constructor(private dashboardService: DashboardService) {}

  ngOnInit() {
    this.loadOverview();
  }

  loadOverview() {
    this.loading = true;
    this.error = null;

    this.dashboardService.getOverview(30).subscribe({
      next: (data) => {
        this.overview = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load dashboard', err);
        this.error = '加载仪表盘数据失败';
        this.loading = false;
      }
    });
  }

  formatDuration(seconds?: number): string {
    if (!seconds) return '0分钟';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}小时${minutes}分钟`;
    }
    return `${minutes}分钟`;
  }
}
