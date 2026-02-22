"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";

export default function AuthLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const router = useRouter();
  const status = useAuthStore((s) => s.status);

  useEffect(() => {
    if (status === "authed") {
      router.replace("/");
    }
  }, [status, router]);

  if (status !== "guest") return null;

  return children;
}
