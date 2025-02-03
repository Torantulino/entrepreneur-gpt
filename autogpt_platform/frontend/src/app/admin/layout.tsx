"use client";

import { useState } from "react";
import Link from "next/link";
import { BinaryIcon, XIcon } from "lucide-react";
import { usePathname } from "next/navigation"; // Add this import

const tabs = [
  { name: "Dashboard", href: "/admin/dashboard" },
  { name: "Marketplace", href: "/admin/marketplace" },
  { name: "Users", href: "/admin/users" },
  { name: "Settings", href: "/admin/settings" },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname(); // Get the current pathname
  const [activeTab, setActiveTab] = useState(() => {
    // Set active tab based on the current route
    return tabs.find((tab) => tab.href === pathname)?.name || tabs[0].name;
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-xs">
        <div className="max-w-10xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <div className="shrink-0">
                <h1 className="text-xl font-bold">Admin Panel</h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {tabs.map((tab) => (
                  <Link
                    key={tab.name}
                    href={tab.href}
                    className={`${
                      activeTab === tab.name
                        ? "border-indigo-500 text-indigo-600"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                    } inline-flex items-center border-b-2 px-1 pt-1 text-sm font-medium`}
                    onClick={() => setActiveTab(tab.name)}
                  >
                    {tab.name}
                  </Link>
                ))}
              </div>
            </div>
            <div className="sm:hidden">
              <button
                type="button"
                className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-hidden focus:ring-2 focus:ring-inset focus:ring-indigo-500"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                <span className="sr-only">Open main menu</span>
                {mobileMenuOpen ? (
                  <XIcon className="block h-6 w-6" aria-hidden="true" />
                ) : (
                  <BinaryIcon className="block h-6 w-6" aria-hidden="true" />
                )}
              </button>
            </div>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="sm:hidden">
            <div className="space-y-1 pb-3 pt-2">
              {tabs.map((tab) => (
                <Link
                  key={tab.name}
                  href={tab.href}
                  className={`${
                    activeTab === tab.name
                      ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                      : "border-transparent text-gray-600 hover:border-gray-300 hover:bg-gray-50 hover:text-gray-800"
                  } block border-l-4 py-2 pl-3 pr-4 text-base font-medium`}
                  onClick={() => {
                    setActiveTab(tab.name);
                    setMobileMenuOpen(false);
                  }}
                >
                  {tab.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </nav>

      <main className="py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
