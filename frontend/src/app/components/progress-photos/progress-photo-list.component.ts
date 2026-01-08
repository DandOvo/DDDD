import { Component, OnInit } from '@angular/core';
import { ProgressPhotoService } from '../../services/progress-photo.service';
import { ProgressPhoto } from '../../models/progress-photo.model';

@Component({
  selector: 'app-progress-photo-list',
  templateUrl: './progress-photo-list.component.html',
  styleUrls: ['./progress-photo-list.component.css']
})
export class ProgressPhotoListComponent implements OnInit {
  photos: ProgressPhoto[] = [];
  loading = true;
  page = 1;
  pageSize = 20;
  total = 0;
  selectedPhotoType: string = 'all';
  showForm = false;
  uploading = false;
  selectedFile: File | null = null;
  formData = {
    photoType: '',
    notes: ''
  };

  constructor(private progressPhotoService: ProgressPhotoService) {}

  ngOnInit() {
    this.loadPhotos();
  }

  loadPhotos() {
    this.loading = true;
    const photoType = this.selectedPhotoType === 'all' ? undefined : this.selectedPhotoType;

    this.progressPhotoService.getList(this.page, this.pageSize, photoType).subscribe({
      next: (response) => {
        this.photos = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Failed to load progress photos', error);
        this.loading = false;
      }
    });
  }

  filterByType(photoType: string) {
    this.selectedPhotoType = photoType;
    this.page = 1;
    this.loadPhotos();
  }

  deletePhoto(id: string) {
    if (confirm('确定要删除这张照片吗？')) {
      this.progressPhotoService.delete(id).subscribe({
        next: () => {
          this.loadPhotos();
        },
        error: (error) => {
          console.error('Failed to delete photo', error);
          alert('删除失败');
        }
      });
    }
  }

  getPhotoTypeLabel(photoType: string): string {
    const labels: { [key: string]: string } = {
      'front': '正面',
      'side': '侧面',
      'back': '背面'
    };
    return labels[photoType] || photoType;
  }

  openPhoto(url: string) {
    window.open(url, '_blank');
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.resetForm();
    }
  }

  resetForm() {
    this.selectedFile = null;
    this.formData = {
      photoType: '',
      notes: ''
    };
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        alert('请选择图片文件');
        return;
      }
      // 验证文件大小 (最大10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('文件大小不能超过10MB');
        return;
      }
      this.selectedFile = file;
    }
  }

  submitForm() {
    if (!this.selectedFile) {
      alert('请选择要上传的照片');
      return;
    }
    if (!this.formData.photoType) {
      alert('请选择照片类型');
      return;
    }

    this.uploading = true;

    this.progressPhotoService.upload(
      this.selectedFile,
      this.formData.photoType,
      new Date(),
      this.formData.notes
    ).subscribe({
      next: () => {
        this.uploading = false;
        this.showForm = false;
        this.resetForm();
        this.loadPhotos();
      },
      error: (error) => {
        console.error('Failed to upload photo', error);
        this.uploading = false;
        alert('上传失败');
      }
    });
  }
}
