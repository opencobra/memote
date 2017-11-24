import { Injectable, Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'olFilter'
})
@Injectable()
export class AttributeFilterPipe implements PipeTransform {
  transform(array: any[], filterString: string ,filterProperty: string): any {
    if (array.length === 0) {
      return array;
    }
    for (var object of array) {
      if (object[filterProperty] === filterString){
        return object[filterProperty];
      }
    }
  }
}
