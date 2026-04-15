import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

interface Link {
  id: number;
  original_url: string;
  short_code: string;
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
  shortenedUrl = '';
  links: Link[] = [];
  copied = false;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadLinks();
  }

  shorten() {
    if (!this.inputUrl) return;
    this.http.post<Link>('/api/shorten', { original_url: this.inputUrl }).subscribe(res => {
      this.shortenedUrl = `${window.location.origin}/${res.short_code}`;
      this.inputUrl = '';
      this.loadLinks();
    });
  }

  loadLinks() {
    this.http.get<Link[]>('/api/links').subscribe(data => this.links = data);
  }

  copy() {
    navigator.clipboard.writeText(this.shortenedUrl);
    this.copied = true;
    setTimeout(() => this.copied = false, 2000);
  }
}