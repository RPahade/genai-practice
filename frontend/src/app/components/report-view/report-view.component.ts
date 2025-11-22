import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { JobService } from '../../services/job.service';

@Component({
    selector: 'app-report-view',
    templateUrl: './report-view.component.html',
    styleUrls: ['./report-view.component.css']
})
export class ReportViewComponent implements OnInit {
    job: any;
    loading = true;
    report: any;

    constructor(
        private route: ActivatedRoute,
        private jobService: JobService
    ) { }

    ngOnInit() {
        this.route.params.subscribe(params => {
            this.jobService.getJob(+params['id']).subscribe(job => {
                this.job = job;
                // Mock report data for now since backend returns job with result containing report_id
                // In a real app, we would fetch the report details using the report_id
                this.report = {
                    job_id: job.id,
                    title: `Report on ${job.topic}`,
                    content: 'This is a generated report based on the research topic. It contains analysis and findings.',
                    citations: { 'Source 1': 'http://example.com', 'Source 2': 'http://test.com' }
                };
                this.loading = false;
            });
        });
    }

    downloadReport() {
        if (this.report) {
            this.jobService.downloadReport(this.report.job_id).subscribe(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `report_${this.report.job_id}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
            });
        }
    }
}
