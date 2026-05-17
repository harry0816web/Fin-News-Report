"use client";

interface DatePickerProps {
  availableDates: string[];
  selectedDate: string;
  onChange: (date: string) => void;
}

function formatDate(dateStr: string): string {
  const [, month, day] = dateStr.split("-");
  return `${parseInt(month)}月${parseInt(day)}日`;
}

export default function DatePicker({ availableDates, selectedDate, onChange }: DatePickerProps) {
  if (availableDates.length === 0) {
    return <p className="text-gray-500 text-sm">暫無歷史資料</p>;
  }

  return (
    <div className="flex flex-wrap gap-2 mb-6">
      {availableDates.map((date) => (
        <button
          key={date}
          onClick={() => onChange(date)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            date === selectedDate
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
          aria-pressed={date === selectedDate}
        >
          {formatDate(date)}
        </button>
      ))}
    </div>
  );
}
