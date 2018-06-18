export class TestDiff {
  public id: string;
  public diff: any;
  public summary: string;
  public title: string;
  public format_type: string;

  constructor(id: string, {diff, summary, title, format_type}: {
      diff: any, summary: string, title: string, format_type: string
    }) {
        this.id = id;
        this.diff = diff;
        this.summary = summary;
        this.title = title;
        this.format_type = format_type;
       }
}
