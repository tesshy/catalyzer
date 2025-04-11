import { sql } from 'drizzle-orm';
import { sqliteTable, integer, text } from "drizzle-orm/sqlite-core";

// 基底フィールド定義
const base = {
  id: text().primaryKey(),
  title: text(),
  description: text('description'),
  created_at: integer({ mode: 'timestamp' }),
  updated_at: integer({ mode: 'timestamp' }),
};

// Users Table
export const user = sqliteTable('user', {
  ...base,

  username: text('username'),
  email: text('email').unique(),
  role: integer('role', { mode: 'number' }).default(0),
  status: integer('status', { mode: 'number' }).default(1),
});

// Organization Table
export const organization = sqliteTable('organization', {
  ...base,
  tags: text({ mode: 'json' }).$type<string[]>().default(sql`'[]'`),
  url: text('url'),
});

// Group Table
export const group = sqliteTable('group', {
  ...base,
  tags: text({ mode: 'json' }).$type<string[]>().default(sql`'[]'`),
  url: text('url'),
});

// Resource Table
export const resource = sqliteTable('resource', {
  ...base,
  tags: text({ mode: 'json' }).$type<string[]>().default(sql`'[]'`),
  url: text('url'),
});


// References
// https://orm.drizzle.team/docs/guides/empty-array-default-value