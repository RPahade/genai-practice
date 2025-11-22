import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { JobService } from '../../services/job.service';

@Component({
    selector: 'app-job-create',
    templateUrl: './job-create.component.html',
    styleUrls: ['./job-create.component.css']
})
export class JobCreateComponent implements OnInit {
    jobForm!: FormGroup;
    loading = false;
    submitted = false;
    error = '';

    selectedFile: File | null = null;

    constructor(
        private formBuilder: FormBuilder,
        private router: Router,
        private jobService: JobService
    ) { }

    ngOnInit() {
        this.jobForm = this.formBuilder.group({
            topic: ['', Validators.required],
            file: [null]
        });
    }

    get f() { return this.jobForm.controls; }

    onFileChange(event: any) {
        if (event.target.files.length > 0) {
            this.selectedFile = event.target.files[0];
        }
    }

    onSubmit() {
        this.submitted = true;

        if (this.jobForm.invalid) {
            return;
        }

        this.loading = true;
        this.jobService.createJob(this.f['topic'].value, this.selectedFile)
            .subscribe(
                data => {
                    this.router.navigate(['/']);
                },
                error => {
                    this.error = error;
                    this.loading = false;
                });
    }
}
