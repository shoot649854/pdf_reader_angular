// import { bootstrapApplication } from '@angular/platform-browser';
// import { appConfig } from './app/app.config';
// import { AppComponent } from './app/app.component';

// import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer';
// import { BrowserModule } from '@angular/platform-browser';
// import { HttpClientModule } from '@angular/common/http'; 

// import { NgModule } from '@angular/core';
// import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
// import { MatButtonModule } from '@angular/material/button';
// import { MatInputModule } from '@angular/material/input';
// import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
// import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
// import { RouterModule } from '@angular/router';
// import { AppModule } from './app/app.module';

// bootstrapApplication(AppComponent, appConfig)
//   .catch((err) => console.error(err));

// platformBrowserDynamic().bootstrapModule(AppModule)
//   .catch(err => console.error(err));

// @NgModule({
//     imports: [
//       BrowserModule,
//       NgxExtendedPdfViewerModule,
//       HttpClientModule,
//       BrowserAnimationsModule,
//       MatButtonModule,
//       MatInputModule,
//       MatProgressSpinnerModule,
//       RouterModule.forRoot([]), 
//     ],
//     bootstrap: [AppComponent]
//   })
//   export class AppModule {}
import { appConfig } from './app/app.config';
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
