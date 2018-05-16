export class TestHistory {
  public id: string;
  public history: any;
  public summary: string;
  public title: string;
  public format_type: string;

  constructor(id: string, {history, summary, title, format_type}: {
      history: any, summary: string, title: string, format_type: string
    }) {
        this.id = id;
        this.history = history;
        this.summary = summary;
        this.title = title;
        this.format_type = format_type;
       }
}
