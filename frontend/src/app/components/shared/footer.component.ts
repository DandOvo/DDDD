// Visual refresh: renamed year field while keeping dynamic year logic
import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent {
  displayYear = new Date().getFullYear();
}
