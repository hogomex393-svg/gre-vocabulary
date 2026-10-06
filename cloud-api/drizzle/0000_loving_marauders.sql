CREATE TABLE `study_states` (
	`id` text PRIMARY KEY NOT NULL,
	`ciphertext` text NOT NULL,
	`iv` text NOT NULL,
	`revision` integer DEFAULT 1 NOT NULL,
	`previous_ciphertext` text,
	`previous_iv` text,
	`created_at` integer NOT NULL,
	`updated_at` integer NOT NULL
);
