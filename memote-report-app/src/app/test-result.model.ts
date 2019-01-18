export class TestResult {
  public id: string;
  public data: any;
  public duration: number;
  public message: string;
  public metric: number;
  public result: string;
  public summary: string;
  public title: string;
  public format_type: string;

  private errorFailsafe(result: string) {
    if (this.result !== 'skipped' && (this.data === null || typeof this.data === 'undefined') ) {
      this.result = 'error';
    } else {
      this.result = result;
    }
  }

  constructor(id: string, {data, duration, message, metric, result, summary, title, format_type}: {
      data: any, duration: number, message: string, metric: number,
      result: string, summary: string, title: string, format_type: string
    }) {
        this.id = id;
        this.data = data;
        this.duration = duration;
        this.message = message;
        this.metric = metric;
        this.errorFailsafe(result);
        this.summary = summary;
        this.title = title;
        this.format_type = format_type;
       }
}
