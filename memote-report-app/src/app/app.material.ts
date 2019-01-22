import {NgModule} from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  MatAutocompleteModule,
  MatButtonModule,
  MatBadgeModule,
  MatCardModule,
  MatCheckboxModule,
  MatDialogModule,
  MatFormFieldModule,
  MatIconModule,
  MatIconRegistry,
  MatInputModule,
  MatListModule,
  MatMenuModule,
  MatSidenavModule,
  MatToolbarModule,
  MatTableModule,
  MatSortModule,
  MatPaginatorModule,
  MatTooltipModule,
  MatProgressBarModule,
  MatGridListModule,
  MatSelectModule,
  MatExpansionModule
} from '@angular/material';


/**
 * https://material.angular.io/guide/getting-started#step-3-import-the-component-modules
 */
@NgModule({
  imports: [ BrowserAnimationsModule, MatBadgeModule, MatButtonModule, MatCheckboxModule, MatListModule, MatToolbarModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatCardModule, MatSidenavModule, MatMenuModule, MatAutocompleteModule,
    MatDialogModule, MatTableModule, MatSortModule, MatPaginatorModule, MatTooltipModule, MatProgressBarModule,
    MatGridListModule, MatSelectModule, MatExpansionModule],
  exports: [ BrowserAnimationsModule, MatBadgeModule, MatButtonModule, MatCheckboxModule, MatListModule, MatToolbarModule, MatIconModule,
    MatFormFieldModule, MatInputModule,
    MatCardModule, MatSidenavModule, MatMenuModule, MatAutocompleteModule, MatDialogModule, MatTableModule, MatSortModule,
    MatPaginatorModule, MatTooltipModule, MatProgressBarModule, MatGridListModule, MatSelectModule, MatExpansionModule]
})
export class AppMaterialModule {
}
