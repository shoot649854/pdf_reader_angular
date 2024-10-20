import { Component, Inject, OnInit, OnDestroy } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { trigger, transition, style, animate } from '@angular/animations';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-warning-popup',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  templateUrl: './warning-popup.component.html',
  styleUrls: ['./warning-popup.component.scss'],
  animations: [
    trigger('popupAnimation', [
      transition(':enter', [
        style({ transform: 'translateY(-100%)', opacity: 0 }),
        animate(
          '300ms ease-out',
          style({ transform: 'translateY(0)', opacity: 1 })
        ),
      ]),
      transition(':leave', [
        animate(
          '300ms ease-in',
          style({ transform: 'translateY(-100%)', opacity: 0 })
        ),
      ]),
    ]),
  ],
})
export class warningPopupComponent implements OnInit, OnDestroy {
  width: string;
  height: string;
  enterAnimationDuration: string;
  exitAnimationDuration: string;

  constructor(
    public dialogRef: MatDialogRef<warningPopupComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    // Set default values
    this.width = data?.width || '400px';
    this.height = data?.height || '1000px';
    this.enterAnimationDuration = data?.enterAnimationDuration || '300ms';
    this.exitAnimationDuration = data?.exitAnimationDuration || '300ms';
  }

  ngOnInit(): void {}

  onClose(): void {
    this.dialogRef.close();
  }

  ngOnDestroy(): void {}
}
