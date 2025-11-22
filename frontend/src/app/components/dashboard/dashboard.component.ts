import { Component, OnInit } from '@angular/core';
import { JobService } from '../../services/job.service';
import { AuthService } from '../../services/auth.service';
import { ThemeService } from '../../services/theme.service';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
    jobs: any[] = [];
    loading = false;

    constructor(
        private jobService: JobService,
        private authService: AuthService,
        public themeService: ThemeService
    ) { }

    ngOnInit() {
        this.loadJobs();
    }

    loadJobs() {
        this.loading = true;
        this.jobService.getJobs().subscribe(jobs => {
            this.jobs = jobs;
            this.loading = false;
        });
    }

    logout() {
        this.authService.logout();
    }

    toggleTheme() {
        this.themeService.toggleTheme();
    }
}
