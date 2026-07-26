"use client";

import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/20/solid';
import clsx from 'clsx';

interface Props {
  currentPage: number;
  pageSize: number;
  totalCount: number;
  onPageChange: (page: number) => void;
}

export default function PaginationControls({ currentPage, pageSize, totalCount, onPageChange }: Props) {
  const totalPages = Math.ceil(totalCount / pageSize);
  const canPrev = currentPage > 1;
  const canNext = currentPage < totalPages;

  const handlePrev = () => {
    if (canPrev) onPageChange(currentPage - 1);
  };
  const handleNext = () => {
    if (canNext) onPageChange(currentPage + 1);
  };

  return (
    <div className="flex items-center justify-between mt-4">
      <button
        onClick={handlePrev}
        disabled={!canPrev}
        className={clsx('flex items-center px-3 py-1 border rounded', {
          'bg-gray-200 text-gray-500 cursor-not-allowed': !canPrev,
          'bg-white hover:bg-gray-100': canPrev,
        })}
      >
        <ChevronLeftIcon className="h-5 w-5 mr-1" /> Prev
      </button>
      <span className="text-sm text-gray-700">
        Page {currentPage} of {totalPages}
      </span>
      <button
        onClick={handleNext}
        disabled={!canNext}
        className={clsx('flex items-center px-3 py-1 border rounded', {
          'bg-gray-200 text-gray-500 cursor-not-allowed': !canNext,
          'bg-white hover:bg-gray-100': canNext,
        })}
      >
        Next <ChevronRightIcon className="h-5 w-5 ml-1" />
      </button>
    </div>
  );
}
