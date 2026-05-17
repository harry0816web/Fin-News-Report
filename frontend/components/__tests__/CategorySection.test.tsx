import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import CategorySection from "../CategorySection";
import type { AnalyzedArticle } from "@/types/news";

const mockArticle: AnalyzedArticle = {
  id: "1",
  title: "測試文章",
  url: "https://example.com",
  source: "測試媒體",
  published_at: "2026-05-16T08:00:00+08:00",
  category: "科技股市",
  summary: "摘要內容",
  impact_analysis: "影響分析",
  sentiment: "neutral",
};

describe("CategorySection", () => {
  it("renders category heading and articles", () => {
    render(<CategorySection category="科技股市" articles={[mockArticle]} />);
    expect(screen.getByText("【科技股市】")).toBeDefined();
    expect(screen.getByText("測試文章")).toBeDefined();
  });

  it("returns null when articles is empty", () => {
    const { container } = render(<CategorySection category="科技股市" articles={[]} />);
    expect(container.firstChild).toBeNull();
  });
});
