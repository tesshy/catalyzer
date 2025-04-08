import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

// Users Table
export const user = sqliteTable('user', {
  id: text('id').primaryKey(),
  username: text('username').notNull(),
  email: text('email').unique(),
  fullname: text('fullname'),
  created_at: integer('created_at', { mode: 'timestamp' }),
  modified_at: integer('modified_at', { mode: 'timestamp' }),
  about: text('about'),
  role: integer('role', { mode: 'number' }).default(0),
  status: integer('status', { mode: 'number' }).default(1),
});
