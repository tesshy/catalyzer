import type { Route } from "./+types/home";
import { Dashboard } from "../components/Dashboard";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Workdesk - DuckLake管理ツール" },
    { name: "description", content: "DuckDBを使用したDataLake管理のためのWebアプリケーション" },
  ];
}

export default function Home() {
  return <Dashboard />;
}
