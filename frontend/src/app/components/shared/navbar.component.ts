// Visual refresh: renamed state fields to match redesigned navigation while keeping behavior intact
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  sessionUser: User | null = null;
  navDrawerOpen = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.authService.currentUser.subscribe(user => {
      this.sessionUser = user;
    });
  }

  signOut(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  toggleNavigation(): void {
    this.navDrawerOpen = !this.navDrawerOpen;
  }

  hasSession(): boolean {
    return this.authService.isLoggedIn();
  }
}
