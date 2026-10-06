import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
export const studyStates = sqliteTable('study_states', {
  id: text('id').primaryKey(),
  ciphertext: text('ciphertext').notNull(),
  iv: text('iv').notNull(),
  revision: integer('revision').notNull().default(1),
  previousCiphertext: text('previous_ciphertext'),
  previousIv: text('previous_iv'),
  createdAt: integer('created_at').notNull(),
  updatedAt: integer('updated_at').notNull(),
});
