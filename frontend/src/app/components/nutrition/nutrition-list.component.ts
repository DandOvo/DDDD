import { Component, OnInit } from '@angular/core';
import { NutritionService } from '../../services/nutrition.service';
import { Nutrition } from '../../models/nutrition.model';

@Component({
  selector: 'app-nutrition-list',
  templateUrl: './nutrition-list.component.html',
  styleUrls: ['./nutrition-list.component.css']
})
export class NutritionListComponent implements OnInit {
  nutritionRecords: Nutrition[] = [];
  loading = true;
  showForm = false;
  formData = {
    mealType: '',
    foodName: '',
    calories: null as number | null,
    protein: null as number | null,
    carbohydrates: null as number | null,
    fat: null as number | null,
    servingSize: '',
    notes: ''
  };

  constructor(private nutritionService: NutritionService) {}

  ngOnInit() {
    this.loadNutrition();
  }

  loadNutrition() {
    this.loading = true;
    this.nutritionService.getList(1, 20).subscribe({
      next: (response) => {
        this.nutritionRecords = response.items;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  delete(id: string) {
    if (confirm('确定要删除吗？')) {
      this.nutritionService.delete(id).subscribe(() => this.loadNutrition());
    }
  }

  toggleForm() {
    this.showForm = !this.showForm;
    if (!this.showForm) {
      this.resetForm();
    }
  }

  resetForm() {
    this.formData = {
      mealType: '',
      foodName: '',
      calories: null,
      protein: null,
      carbohydrates: null,
      fat: null,
      servingSize: '',
      notes: ''
    };
  }

  submitForm() {
    if (!this.formData.foodName || !this.formData.mealType) {
      alert('请填写食物名称和餐次');
      return;
    }

    const data: any = {
      mealType: this.formData.mealType,
      foodName: this.formData.foodName,
      recordedAt: new Date().toISOString()
    };

    if (this.formData.calories) data.calories = this.formData.calories;
    if (this.formData.protein) data.protein = this.formData.protein;
    if (this.formData.carbohydrates) data.carbohydrates = this.formData.carbohydrates;
    if (this.formData.fat) data.fat = this.formData.fat;
    if (this.formData.servingSize) data.servingSize = this.formData.servingSize;
    if (this.formData.notes) data.notes = this.formData.notes;

    this.nutritionService.create(data).subscribe({
      next: () => {
        this.showForm = false;
        this.resetForm();
        this.loadNutrition();
      },
      error: (error) => {
        console.error('Failed to create nutrition record', error);
        alert('添加失败');
      }
    });
  }
}
