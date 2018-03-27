export class TestHistory {
  public id: string;
  public history: any;
  public summary: string;
  public title: string;
  public type: string;

  constructor(id: string, {history, summary, title, type}: {
      history: any, summary: string, title: string, type: string
    }) {
        this.id = id;
        this.history = history;
        this.summary = summary;
        this.title = title;
        this.type = type;
       }
}
