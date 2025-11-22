import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class JobService {
    private apiUrl = 'http://localhost:8000'; // Should use environment

    constructor(private http: HttpClient) { }

    getJobs(): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/jobs/`);
    }

    createJob(topic: string, file: File | null): Observable<any> {
        const formData = new FormData();
        formData.append('topic', topic);
        if (file) {
            formData.append('file', file);
        }
        return this.http.post<any>(`${this.apiUrl}/jobs/`, formData);
    }

    getJob(id: number): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/jobs/${id}`);
    }

    downloadReport(jobId: number): Observable<Blob> {
        return this.http.get(`${this.apiUrl}/jobs/${jobId}/download`, { responseType: 'blob' });
    }
}
