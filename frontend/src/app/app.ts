import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpErrorResponse } from '@angular/common/http';

interface Link {
  id: number;
  original_url: string;
  short_code: string;
  is_custom: boolean;
  created_at: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit {
  inputUrl = '';
  customCode = '';
  shortenedUrl = '';
  links: Link[] = [];
  copied = false;
  errorMessage = '';
  loading = false;
  loadingLinks = false;
  offset = 0;
  readonly pageSize = 10;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadLinks();
  }

  shorten() {
    if (!this.inputUrl.trim()) return;
    this.loading = true;
    this.errorMessage = '';

    this.http.post<Link>('/api/shorten', {
      original_url: this.inputUrl,
      custom_code: this.customCode || null
    }).subscribe({
      next: (res) => {
        this.shortenedUrl = `${window.location.origin}/${res.short_code}`;
        this.inputUrl = '';
        this.customCode = '';
        this.offset = 0;
        this.loadLinks();
      },
      error: (err: HttpErrorResponse) => {
        this.errorMessage = this.mapError(err);
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  loadLinks() {
    this.loadingLinks = true;
    this.http.get<Link[]>(`/api/links?limit=${this.pageSize}&offset=${this.offset}`).subscribe({
      next: (data) => {
        this.links = data;
      },
      error: () => {
        this.errorMessage = 'Failed to load links. Please try again.';
      },
      complete: () => {
        this.loadingLinks = false;
      }
    });
  }

  previousPage() {
    if (this.offset === 0) return;
    this.offset = Math.max(0, this.offset - this.pageSize);
    this.loadLinks();
  }

  nextPage() {
    if (this.links.length < this.pageSize) return;
    this.offset += this.pageSize;
    this.loadLinks();
  }

  copy() {
    navigator.clipboard.writeText(this.shortenedUrl);
    this.copied = true;
    setTimeout(() => this.copied = false, 2000);
  }

  private mapError(err: HttpErrorResponse): string {
    if (err.status === 409) {
      return 'This custom alias is already taken. Please choose another one.';
    }
    if (err.status === 422 || err.status === 400) {
      return 'Please enter a valid URL (http:// or https://) and alias format.';
    }
    if (err.status >= 500) {
      return 'Server error. Please try again in a moment.';
    }
    return 'Request failed. Please verify your data and try again.';
  }
}