import type { AnalyzedArticle } from "@/types/news";
import ArticleCard from "./ArticleCard";

interface CategorySectionProps {
  category: string;
  articles: AnalyzedArticle[];
}

export default function CategorySection({ category, articles }: CategorySectionProps) {
  if (articles.length === 0) return null;

  return (
    <section className="mb-8">
      <h2 className="text-lg font-bold text-gray-800 mb-3 pb-2 border-b border-gray-200">
        【{category}】
      </h2>
      <div className="space-y-3">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </section>
  );
}
