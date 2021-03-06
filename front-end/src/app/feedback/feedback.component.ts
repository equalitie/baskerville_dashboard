import {Component, OnInit, ViewChild} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {FeedbackContextVM, FeedbackContextTypeEnum, FeedbackContext} from '../_models/models';
import {BaskervilleService} from '../_services/baskerville.service';
import {NotificationService} from '../_services/notification.service';
import {MatStepper} from '@angular/material/stepper';


@Component({
  selector: 'app-feedback',
  templateUrl: './feedback.component.html',
  styleUrls: ['./feedback.component.css']
})
export class FeedbackComponent implements OnInit {
  @ViewChild('stepper') stepper: MatStepper;
  contextFormGroup: FormGroup;
  resultsFormGroup: FormGroup;
  selectedFeedbackContext: FeedbackContext;
  feedbackContextVM: FeedbackContextVM;
  inProgress = false;
  submitted = false;
  constructor(
    private formBuilder: FormBuilder,
    private baskervilleSvc: BaskervilleService,
    private notificationSvc: NotificationService,
    ) {
    this.feedbackContextVM = new FeedbackContextVM({});
    this.selectedFeedbackContext = null;
  }
  ngOnInit(): void {
    this.setFeedbackContextVM();
    this.contextFormGroup = this.formBuilder.group({
      fc: ['', ],

    });
    this.resultsFormGroup = this.formBuilder.group({
      secondCtrl: ['', Validators.required]
    });
  }
  setFeedbackContextVM(): void {
    this.baskervilleSvc.getFeedbackContentVM().subscribe(
      data => {
        if (data.success) {
          console.warn(data);
          this.feedbackContextVM = new FeedbackContextVM(data.data);
          this.notificationSvc.showSnackBar(data.message);
          console.warn(this.feedbackContextVM);
        }
      },
      e => {
        this.notificationSvc.showSnackBar(e.message);
      }
    );
  }
  onCreated(success): void {
    if (success){
      this.submitted = false;
      this.selectedFeedbackContext = this.baskervilleSvc.selectedFeedback;
      this.stepper.next();
    }
  }
  fcChange(e: boolean): void {
    this.submitted = false;
    this.baskervilleSvc.selectedFeedback = this.feedbackContextVM.idToFc[this.contextFormGroup.controls.fc.value];
    this.selectedFeedbackContext = this.baskervilleSvc.selectedFeedback;
    this.stepper.next();
  }
  feedbackChange(e: boolean): void {
    this.submitted = false;
    this.inProgress = false;
  }
  submitToBaskerville(): void {
    this.submitted = true;
    this.inProgress = true;
    this.baskervilleSvc.setInProgress(this.inProgress);
    this.baskervilleSvc.sumbitToBaskerville().subscribe(
      data => {
        this.notificationSvc.showSnackBar(data.message);
        this.submitted = true;
        this.inProgress = false;
        this.baskervilleSvc.setInProgress(this.inProgress);
      },
      e => {
        this.notificationSvc.showSnackBar(e.message);
        this.submitted = false;
        this.inProgress = false;
        this.baskervilleSvc.setInProgress(this.inProgress);
      }
    );
  }
}

