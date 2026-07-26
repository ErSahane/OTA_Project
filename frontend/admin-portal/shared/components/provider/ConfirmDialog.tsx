"use client"

import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useEffect } from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

type Variant = 'primary' | 'danger' | 'neutral';

interface Props {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmVariant?: Variant;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'primary',
  onConfirm,
  onCancel,
  loading = false,
}: Props) {
  // Return focus to the previously active element when dialog closes
  useEffect(() => {
    if (!open) {
      const el = document.activeElement as HTMLElement | null;
      el?.blur();
    }
  }, [open]);

  const variantClasses: Record<Variant, string> = {
    primary: 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-400',
    danger:  'bg-red-600 hover:bg-red-700 focus:ring-red-400',
    neutral: 'bg-slate-600 hover:bg-slate-700 focus:ring-slate-400',
  };

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onCancel}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-slate-800 p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-start gap-3 mb-4">
                  <ExclamationTriangleIcon className="h-6 w-6 text-amber-500 flex-shrink-0" />
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-slate-900 dark:text-slate-100">
                    {title}
                  </Dialog.Title>
                </div>
                <Dialog.Description className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                  {message}
                </Dialog.Description>

                <div className="mt-6 flex justify-end gap-3">
                  <button
                    type="button"
                    className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
                    onClick={onCancel}
                    disabled={loading}
                  >
                    {cancelLabel}
                  </button>
                  <button
                    type="button"
                    className={`inline-flex justify-center rounded-lg px-4 py-2 text-sm font-semibold text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 disabled:opacity-50 ${variantClasses[confirmVariant]}`}
                    onClick={onConfirm}
                    disabled={loading}
                  >
                    {loading ? (
                      <svg className="h-4 w-4 animate-spin mr-2" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                      </svg>
                    ) : null}
                    {confirmLabel}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
