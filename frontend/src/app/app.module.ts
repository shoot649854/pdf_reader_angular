import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

// Angular Material imports
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

// ngx-extended-pdf-viewer import
import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer';

// Components
import { AppComponent } from './app.component';
import { PdfViewerComponent } from '../components/pdf-viewer/pdf-viewer.component';
import { PdfUploadComponent } from '../components/pdf-upload/pdf-upload.component';
import { PdfEditorComponent } from '../components/pdf-editor/pdf-editor.component';

import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [AppComponent, PdfViewerComponent, PdfUploadComponent, PdfEditorComponent],
  imports: [
    RouterModule.forRoot([]),
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    NgxExtendedPdfViewerModule,

    // Material Modules
    MatToolbarModule,
    MatProgressBarModule,
    MatSnackBarModule,
    MatButtonModule,
    MatIconModule,
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
