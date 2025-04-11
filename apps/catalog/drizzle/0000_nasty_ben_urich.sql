CREATE TABLE `group` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text,
	`description` text,
	`created_at` integer,
	`updated_at` integer,
	`tags` text DEFAULT '[]',
	`url` text
);
--> statement-breakpoint
CREATE TABLE `organization` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text,
	`description` text,
	`created_at` integer,
	`updated_at` integer,
	`tags` text DEFAULT '[]',
	`url` text
);
--> statement-breakpoint
CREATE TABLE `resource` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text,
	`description` text,
	`created_at` integer,
	`updated_at` integer,
	`tags` text DEFAULT '[]',
	`url` text
);
--> statement-breakpoint
CREATE TABLE `user` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text,
	`description` text,
	`created_at` integer,
	`updated_at` integer,
	`username` text,
	`email` text,
	`role` integer DEFAULT 0,
	`status` integer DEFAULT 1
);
--> statement-breakpoint
CREATE UNIQUE INDEX `user_email_unique` ON `user` (`email`);