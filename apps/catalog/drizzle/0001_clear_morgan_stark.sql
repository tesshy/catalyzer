CREATE TABLE `user` (
	`id` text PRIMARY KEY NOT NULL,
	`username` text NOT NULL,
	`email` text,
	`fullname` text,
	`created_at` integer,
	`modified_at` integer,
	`about` text,
	`role` integer DEFAULT 0,
	`status` integer DEFAULT 1
);
--> statement-breakpoint
CREATE UNIQUE INDEX `user_email_unique` ON `user` (`email`);--> statement-breakpoint
DROP TABLE `guestBook`;