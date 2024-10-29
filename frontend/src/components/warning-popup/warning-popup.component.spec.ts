import { ComponentFixture, TestBed } from '@angular/core/testing';

import { warningPopupComponent } from './warning-popup.component';

describe('warningPopupComponent', () => {
  let component: warningPopupComponent;
  let fixture: ComponentFixture<warningPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [warningPopupComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(warningPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
