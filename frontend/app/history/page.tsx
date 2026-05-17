"use client";

import { useEffect, useReducer, useState } from "react";
import { fetchAvailableDates, fetchNews } from "@/lib/api";
import type { DailyDigest, Category } from "@/types/news";
import DatePicker from "@/components/DatePicker";
import CategorySection from "@/components/CategorySection";
import LoadingSkeleton from "@/components/LoadingSkeleton";

const CATEGORY_ORDER: Category[] = ["科技股市", "總體經濟", "上市公司公告", "國際財經"];

type FetchState = { loading: boolean; digest: DailyDigest | null };
type FetchAction =
  | { type: "fetch_start" }
  | { type: "fetch_done"; digest: DailyDigest | null };

function fetchReducer(_: FetchState, action: FetchAction): FetchState {
  switch (action.type) {
    case "fetch_start":
      return { loading: true, digest: null };
    case "fetch_done":
      return { loading: false, digest: action.digest };
  }
}

export default function HistoryPage() {
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [{ loading, digest }, dispatch] = useReducer(fetchReducer, {
    loading: false,
    digest: null,
  });

  useEffect(() => {
    fetchAvailableDates().then((dates) => {
      setAvailableDates(dates);
      if (dates.length > 0) {
        setSelectedDate(dates[0]);
      }
    });
  }, []);

  useEffect(() => {
    if (!selectedDate) return;
    dispatch({ type: "fetch_start" });
    fetchNews(selectedDate).then((data) => {
      dispatch({ type: "fetch_done", digest: data });
    });
  }, [selectedDate]);

  const groupedArticles = digest
    ? CATEGORY_ORDER.reduce<Record<string, typeof digest.articles>>(
        (acc, cat) => {
          acc[cat] = digest.articles.filter((a) => a.category === cat);
          return acc;
        },
        {}
      )
    : {};

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">歷史新聞</h1>
      <DatePicker
        availableDates={availableDates}
        selectedDate={selectedDate}
        onChange={setSelectedDate}
      />
      {loading && <LoadingSkeleton />}
      {!loading && digest && (
        <div>
          {CATEGORY_ORDER.map((category) => (
            <CategorySection
              key={category}
              category={category}
              articles={groupedArticles[category] ?? []}
            />
          ))}
        </div>
      )}
      {!loading && !digest && selectedDate && (
        <p className="text-gray-500 text-center py-12">此日期無資料</p>
      )}
    </div>
  );
}
