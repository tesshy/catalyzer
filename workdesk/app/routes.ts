import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("import", "routes/import.tsx"),
  route("query", "routes/query.tsx"),
  route("catalog", "routes/catalog.tsx"),
] satisfies RouteConfig;
