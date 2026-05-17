export type Sentiment = "positive" | "negative" | "neutral";

export type Category =
  | "科技股市"
  | "總體經濟"
  | "上市公司公告"
  | "國際財經";

export interface AnalyzedArticle {
  id: string;
  title: string;
  url: string;
  source: string;
  published_at: string; // ISO 8601
  category: Category;
  summary: string;
  impact_analysis: string;
  sentiment: Sentiment;
}

export interface DailyDigest {
  date: string; // "YYYY-MM-DD"
  generated_at: string;
  article_count: number;
  articles: AnalyzedArticle[];
}

export interface Subscriber {
  email: string;
  subscribed_at: string;
}
